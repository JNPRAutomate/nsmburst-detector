"""
Microburst detection tool for ASIC-based NetScreen platforms
"""
import socket
import paramiko
import time
import sys
import re
import select

#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

ASICList = { "NetScreen-5400-II": { "productString":"NetScreen-5400-II","asic_list": [1,2,3,4,5,6], "qmu_list":[1,2,4,6,7,9]}, "NetScreen-5400-III": { "productString":"NetScreen-5400-III","asic_list": [1,2,3,4,5,6], "qmu_list":[1,2,4,6,7,9]}, "NetScreen-1000": { "productString":"NetScreen-1000", "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }, "NetScreen-2000": { "productString":"NetScreen-2000", "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }}
BUFFERList = {"1":["CPU2-d"], "2":["CPU1-d","RSM1-d"],"4":["L2Q-d"],"6":["SLU-d","SLI-d"],"7":["XMT1-d","XMT2-d","XMT3-d","XMT4-d","XMT5-d","XMT6-d","XMT7-d","XMT8-d"],"9":["RSM2-d","CPU3-d","CPU4-d","CPU5-d"]}
BUFFERExp = {"id":["a","..."]}

class HostParser:
    def __init__(self, sourceFile):
        self.sourceFile = sourceFile
        self.hostList = [] # host,username,password
        self.currentHost = 0
        self._parse()
    def _parse(self):
        '''parse host file'''
        try:
            openFile = open(self.sourceFile)
            lines = openFile.readlines()
            openFile.close()
            commentLineRE = re.compile("^#.*|^//.*")
            newlineOnlyRE = re.compile("^\n$")
            for line in lines:
                if commentLineRE.match(line):
                    '''Comment ignoring line'''
                else:
                    lineItems = line.split(",")
                    if len(lineItems) == 3 and lineItems[0] != "" and lineItems[1] != "" and lineItems[2] != "":
                        if newlineOnlyRE.match(lineItems[0]) or newlineOnlyRE.match(lineItems[1]) or newlineOnlyRE.match(lineItems[2]):
                            '''carrige return only found'''
                        else:
                            self.hostList.append({"host":lineItems[0].rstrip(),"username":lineItems[1].rstrip(),"password":lineItems[2].rstrip()})
                    else:
                        '''Ignore line'''
        except:
            raise Exception("Unable to open file")
    def getHosts(self):
        '''return the current hostList'''
        return self.hostList

class NetScreenAgent:
    def __init__(self,hostname,username,password,output):
        """Initalize the object with the correct hostname,username, and password"""
        self.systemFacts = {"hostname":"","product":"","serialNumber":"","controlNumber":"","version":"","type":""}
        self.remoteHost = hostname
        self.promptEnding = "->"
        self.promptRegex = re.compile(".*->")
        self.username = username
        self.password = password
        self.platform = ""
        self.asicCounters = dict()
        if output:
            self.output = output
        else:
            self.output = False

    def connect(self):
        """Create a connection to the remote device"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        try:
            self.socket.connect((self.remoteHost,22))
            self.transport = paramiko.Transport(self.socket)
            self.transport.start_client()
            self.transport.auth_password(username=self.username,password=self.password)
            self.chan = self.transport.open_session()
            self.chan.set_combine_stderr(False)
            self.chan.setblocking(blocking=1)
            self.chan.settimeout(None)
            self.chan.get_pty(term='vt100', width=80, height=24)
            self.chan.invoke_shell()
            self._disablePaging()
        except:
            raise Exception("Unable to connect to host: %s" % (self.remoteHost))

    def _runSilentCommand(self,command,maxMatch):
        """Run a command and supress any output, used for simple housekeeping tasks"""
        self.chan.send(command + "\n")
        coutstr=""
        result=""
        promptMatch = 0
        while True:
            coutstr = self.chan.recv(1024)
            result += coutstr
            if len(coutstr) < 1024:
                lines = result.splitlines()
                for line in lines:
                    #print "SILENT " + line
                    if self.promptRegex.match(line):
                        promptMatch = promptMatch + 1
                        if promptMatch == maxMatch:
                            return

    def _disablePaging(self):
        """disables paging on the console to prevent the need to interact with a pagnated set of output"""
        self._runSilentCommand("set console page 0",2)

    def _enablePaging(self):
        """disables paging on the console to prevent the need to interact with a pagnated set of output"""
        self._runSilentCommand("set console page 20",1)

    def runCommand(self,command):
        """Run a specified command against the device, returns the output of the command"""
        #validate connected before running command
        self.chan.send(command + "\n")
        coutstr=""
        result=""
        finalOutput = ""
        promptMatch = 0
        lineCount = 0
        while True:
            coutstr = self.chan.recv(1024)
            result += coutstr
            if len(coutstr) < 1024:
                lines = result.splitlines()
                for line in lines:
                    lineCount = lineCount + 1
                    if self.promptRegex.match(line):
                        promptMatch = promptMatch + 1
                        if promptMatch == 1:
                            return finalOutput
                    elif lineCount == 1:
                        """Skip processing this line"""
                    else:
                        finalOutput = finalOutput + line + "\n"

    def getSystemFacts(self):
        """Gets all of the needed system facts"""
        self.getHostname()
        self.checkPlatform()

    def getHostname(self):
        """Get system hostname"""
        hostnameMatch = "Hostname: ([\w\W]+)"
        hostnameMatchRe = re.compile(hostnameMatch)

        output = self.runCommand("get hostname")
        splitLines = output.splitlines()
        for line in splitLines:
            if hostnameMatchRe.match(line):
                result = hostnameMatchRe.match(line)
                self.systemFacts["hostname"] = result.group(1)


    def checkPlatform(self):
        """Determine the local platform type"""

        # Product Name: NetScreen-5400-III
        systemMatch = "Product Name: ([\w\W]+)"
        systemMatchRe = re.compile(systemMatch)

        # Serial Number: 0047122010000025, Control Number: 00000000
        serialNumberMatch = "Serial Number: ([\d]+), Control Number: ([\d]+)"
        serialNumberMatchRe = re.compile(serialNumberMatch)

        #Software Version: 6.2.0r9-cu4.0, Type: Firewall+VPN
        softwareVersionMatch = "Software Version: ([\w\W]+), Type: ([\w\W]+)"
        softwareVersionMatchRe = re.compile(softwareVersionMatch)

        output = self.runCommand("get system")
        splitLines = output.splitlines()
        for line in splitLines:
            if systemMatchRe.match(line):
                #
                result = systemMatchRe.match(line)
                self.systemFacts["product"] = result.group(1)
            elif serialNumberMatchRe.match(line):
                #
                result = serialNumberMatchRe.match(line)
                self.systemFacts["serialNumber"] = result.group(1)
                self.systemFacts["controlNumber"] = result.group(2)
            elif softwareVersionMatchRe.match(line):
                #
                result = softwareVersionMatchRe.match(line)
                self.systemFacts["version"] = result.group(1)
                self.systemFacts["type"] = result.group(2)

    def _getAsicCounters(self,asicid,qmuid):
        """Get the counters from the specified asic"""
        if self.systemFacts["product"] == "":
            print "Product facts not gathered"
        elif self.systemFacts["product"] == ASICList["NetScreen-2000"]["productString"] or self.systemFacts["product"] == ASICList["NetScreen-1000"]["productString"]:
            output = self.runCommand("get asic engine qmu pktcnt %s" % (qmuid))
            return output
        elif self.systemFacts["product"] == ASICList["NetScreen-5400-II"]["productString"] or self.systemFacts["product"] == ASICList["NetScreen-5400-III"]["productString"]:
            output = self.runCommand("get asic %s engine qmu pktcnt %s" % (asicid,qmuid))
            return output

    def _compileAsicDict(self,endValues,asicid,queueList,runid,lines):
        """parse asic data"""
        for queue in queueList:
            if queue in endValues[asicid]:
                """queue initilized already"""
            else:
                endValues[asicid][queue] = {}

            if runid in endValues[asicid][queue]:
                """runid initalized already"""
            else:
                endValues[asicid][queue][runid] = ""

            queueRE = re.compile("pktcnt\[%s\s+\]\s=\s(0x\d{8})\s+(\d*)" % (queue))
            for line in lines:
                if queueRE.match(line):
                    matchResult = queueRE.match(line)
                    endValues[asicid][queue][runid] = matchResult.group(1)

            return endValues

    def getAllAsicCounters(self):
        """Get all counters from the platform"""
        #itterate through the asics and the counters on the platform
        asic_list = ASICList[self.systemFacts["product"]]["asic_list"]
        qmu_list = ASICList[self.systemFacts["product"]]["qmu_list"]
        endValues = dict()
        runid = "0"
        for asic in asic_list:
            endValues[asic] = {}
            for qmu in qmu_list:
                self._getAsicCounters(asic,qmu)
                output = self._getAsicCounters(asic,qmu)
                lines = output.split("\n")
                queueList = BUFFERList[str(qmu)]
                endValues = self._compileAsicDict(endValues,asic,queueList,runid,lines)
        runid = "1"
        #sleep for 2 seconds to grab diff of queues
        time.sleep(2)
        for asic in asic_list:
            for qmu in qmu_list:
                self._getAsicCounters(asic,qmu)
                output = self._getAsicCounters(asic,qmu)
                lines = output.split("\n")
                queueList = BUFFERList[str(qmu)]
                endValues = self._compileAsicDict(endValues,asic,queueList,runid,lines)
        self.asicCounters = endValues
        return endValues

    def compareAsicCounters(self):
        """compare the two asic values"""
        for asic in self.asicCounters:
            for queue in self.asicCounters[asic]:
                runid0 = ""
                runid1 = ""
                if "0" in self.asicCounters[asic][queue]:
                    """queue initilized already"""
                    runid0 = self.asicCounters[asic][queue]["0"]

                if "1" in self.asicCounters[asic][queue]:
                    """queue initilized already"""
                    runid1 = self.asicCounters[asic][queue]["1"]

                if runid1 != "" and runid0 != "":
                    asicDiff = int(runid0,0) - int(runid1,0)
                    if asicDiff > 0:
                        if self.output:
                            print "Packet loss of %s packet(s) detected in ASIC %s witin queue %s on host %s" % (asicDiff,asic,queue,self.systemFacts["hostname"])

    def disconnect(self):
        """Disconnect from the device"""
        self._enablePaging()
        self.chan.close()
        self.transport.close()
        self.socket.close()
