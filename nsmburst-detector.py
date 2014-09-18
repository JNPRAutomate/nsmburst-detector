"""
Microburst detection tool for ASIC-based NetScreen platforms
"""
import socket
import paramiko
import sys
import re
import select

#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

ASICList = { "ns5000Mgmt3": { "productString":"NetScreen-5400-III","asic_list": [0,1,2,3,4,5], "qmu_list":[1,2,4,6,7,9]}, "isg1000": { "productString":"NetScreen-1000", "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }, "isg2000": { "productString":"NetScreen-2000", "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }}

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
        if output:
            self.output = output
        else:
            self.output = false

    def connect(self):
        """Create a connection to the remote device"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    print "SILENT " + line
                    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
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

    def getAsicCountners(self,asicid,qmuid):
        """Get the counters from the specified asic"""
        if self.systemFacts["product"] == "":
            print "Product facts not gathered"
        elif self.systemFacts["product"] == ASICList["isg2000"]["productString"]:
            output = self.runCommand("get asic engine qmu pktcnt %s" % ("6"))
            print output
        elif self.systemFacts["product"] == ASICList["isg1000"]["productString"]:
            self.runCommand("get asic engine qmu pktcnt %s" % ("6"))
        elif self.systemFacts["product"] == ASICList["ns5000Mgmt3"]["productString"]:
            self.runCommand("get asic %s engine qmu pktcnt %s" % (asicidmqmuid))

    def getAllAsicCounters(self):
        """Get all counters from the platform"""
        print "foo"
        #itterate through the asics and the counters on the platform


    def disconnect(self):
        """Disconnect from the device"""
        self._enablePaging()
        self.chan.close()
        self.transport.close()
        self.socket.close()

agent = NetScreenAgent("172.22.152.24","netscreen","netscreen",True)
#agent = NetScreenAgent("10.0.1.222","netscreen","netscreen",True)
agent.connect()
agent.getSystemFacts()
print agent.systemFacts
agent.getAsicCountners("","")
agent.disconnect()
