#!/usr/bin/env python
"""
Microburst detection tool for ASIC-based NetScreen platforms
"""
import socket
import paramiko
import time
import sys
import re
import select
import exceptions
import sys
import datetime
#non-module imports
import argparse
import getpass

#used to enable SSH debugging
#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

#Global settings

#The asic and queue mapping data structure. Used for specifing ASICs to check per playtform
ASICList = { "NetScreen-5400-II": { "productString":"NetScreen-5400-II","asic_list": [0,1,2,3,4,5], "qmu_list":[1,2,4,6,7,9]}, "NetScreen-5400-III": { "productString":"NetScreen-5400-III","asic_list": [0,1,2,3,4,5], "qmu_list":[1,2,4,6,7,9]}, "NetScreen-5200": { "productString":"NetScreen-5200","asic_list": [0,1], "qmu_list":[1,2,4,6,7,9]}, "NetScreen-5200-II": { "productString":"NetScreen-5200-II","asic_list": [0,1], "qmu_list":[1,2,4,6,7,9]}, "NetScreen-ISG1000": { "productString":"NetScreen-ISG1000", "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }, "NetScreen-2000": { "productString":"NetScreen-2000", "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }}
#The buffer list data structure specifies which queues to look at for each qmu
BUFFERList = {"1":["CPU2-d"], "2":["CPU1-d","RSM1-d"],"4":["L2Q-d"],"6":["SLU-d","SLI-d"],"7":["XMT1-d","XMT2-d","XMT3-d","XMT4-d","XMT5-d","XMT6-d","XMT7-d","XMT8-d"],"9":["RSM2-d","CPU3-d","CPU4-d","CPU5-d"]}

class OutputLogger:
    """
    OutputLogger

    Handles writing to a file and priting output
    """
    def __init__(self,output,outputFile=""):
        """Initializes all of the bufferes for logging"""
        self.printStdout = output
        self.outputFileName = outputFile
        self.prefix = []
        self.suffix = []
        if self.outputFileName != "":
            self._openFile()

    def _openFile(self):
        """Opens a file for writing"""
        self.outputFile = open(self.outputFileName, 'w')

    def addPrefix(self,newPrefix):
        """Appends a prefix to the output. Each prefix added is put into a list. When a prefix is output each element is seperated by a space. The prefix is added to the front of the output after the timestamp"""
        self.prefix.append(newPrefix)

    def clearPrefix(self):
        """Removes prefixes from logger"""
        self.prefix = []

    def clearSuffix(self):
        """Removes suffix from logger"""
        self.suffix = []

    def addSuffix(self,newSuffix):
        """Appends a suffix to the output. Each suffix added is put into a list. When a suffix is output each element is seperated by a space. The suffix is added to the end of the output."""
        self.suffix.append(newPrefix)

    def _closeFile(self):
        self.outputFile.close()

    def start(self,outputFile=""):
        """Prepares the logger to start logging by opening the file to write to"""
        self.outputFileName = outputFile
        if self.outputFileName != "":
            self._openFile()

    def stop(self):
        """Stops the logger by closing the file"""
        if self.outputFileName != "":
            self._closeFile()

    def log(self,message,timestamp=False):
        """Logs a message with an optional timestamp"""
        baseMessage = message

        message = message.rstrip()

        if len(self.prefix) > 0:
            finalPrefix = " ".join(self.prefix)
            message = "%s %s" % (finalPrefix,message)

        if len(self.suffix) > 0:
            finalSuffix = finalPrefix = " ".join(self.suffix)
            message = "%s %s" % (message,finalSuffix)

        if timestamp:
            message = datetime.datetime.now().isoformat() + " " + message

        if baseMessage != "" and baseMessage != "\n" and len(baseMessage) > 0:
            if self.printStdout:
                print message
            if self.outputFileName != "":
                self.outputFile.write(message + "\n")

class HostParser:
    """
    HostParser

    This class is designed to parse a CSV file containing the host,
     username and password for devices that the user wishes to connect to.

    Input CSV Example:
    #Comment lines start with #
    //Comments can also start with C flavored comments as well
    #IP,username,password example
    1.2.3.4,foo,bar
    #hostname,username,password
    nshost.example.com,netscreen,netscreen

    """
    def __init__(self, sourceFile):
        """When creating the class you must specify the source file location"""
        self.sourceFile = sourceFile
        self.hostList = [] # host,username,password
        self.currentHost = 0
        self._parse()
    def _parse(self):
        """parse host file"""
        try:
            """Try to open the file for reading"""
            openFile = open(self.sourceFile)
            lines = openFile.readlines()
            openFile.close()
            """Comment line regex matches"""
            commentLineRE = re.compile("^#.*|^//.*")
            newlineOnlyRE = re.compile("^\n$")
            for line in lines:
                if commentLineRE.match(line):
                    """Comment ignoring line"""
                    pass
                else:
                    """parse lines"""
                    lineItems = line.split(",")
                    if len(lineItems) == 3 and lineItems[0] != "" and lineItems[1] != "" and lineItems[2] != "":
                        if newlineOnlyRE.match(lineItems[0]) or newlineOnlyRE.match(lineItems[1]) or newlineOnlyRE.match(lineItems[2]):
                            """carrige return only found"""
                            pass
                        else:
                            self.hostList.append({"host":lineItems[0].rstrip(),"username":lineItems[1].rstrip(),"password":lineItems[2].rstrip()})
                    elif len(lineItems) == 1 and lineItems[0] == "" and lineItems[1] == "" and lineItems[2] == "":
                        """Only host was specified"""
                        if newlineOnlyRE.match(lineItems[0]) or newlineOnlyRE.match(lineItems[1]) or newlineOnlyRE.match(lineItems[2]):
                            """carrige return only found"""
                            pass
                        else:
                            self.hostList.append({"host":lineItems[0].rstrip(),"username":"","password":""})
                    else:
                        """Ignore line"""
                        pass
        except:
            raise Exception("Unable to open file")
    def getHosts(self):
        """return the current hostList as a list of dicts"""
        return self.hostList

class NetScreenAgent:
    def __init__(self,hostname,username,password,output,clear_session):
        """Initalize the object with the correct hostname,username, and password"""
        self.systemFacts = {"hostname":"","product":"","serialNumber":"","controlNumber":"","version":"","type":""}
        self.remoteHost = hostname
        self.promptEnding = "->"
        self.promptRegex = re.compile(".*->")
        self.username = username
        self.password = password
        self.platform = ""
        self.asicCounters = dict()
        self.clear_session = clear_session
        if output:
            self.output = output
        else:
            self.output = False

    def connect(self):
        """Create a connection to the remote device"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(15)
        try:
            #Connect to the remote socket
            self.socket.connect((self.remoteHost,22))
            #Start the ssh transport
            self.transport = paramiko.Transport(self.socket)
            self.transport.start_client()
            self.transport.auth_password(username=self.username,password=self.password)
            #Open a new channel to the ssh host
            self.chan = self.transport.open_session()
            self.chan.set_combine_stderr(False)
            self.chan.setblocking(blocking=1)
            self.chan.settimeout(None)
            self.chan.invoke_shell()
            #Wait until the channel is ready, helpful for slow links
            while self.chan.send_ready() != True:
                pass

            if self.clear_session == True:
                self._clear_admin_sessions()

            self._disablePaging()

        except:
            """Raise an exception that a connection is unable to be made"""
            raise Exception("Unable to connect to host: %s" % (self.remoteHost))

    def _runSilentCommand(self,command,maxMatch):
        """Run a command and supress any output, used for simple housekeeping tasks"""
        #sleep to slow the input to the device
        time.sleep(0.2)
        self.chan.send(command + "\n")
        coutstr=""
        result=""
        promptMatch = 0
        while True:
            #Gather the output from the command until the prompt is detected
            if self.chan.recv_ready():
                coutstr = self.chan.recv(1024)
                result += coutstr
                if len(coutstr) < 1024:
                    lines = result.splitlines()
                    for line in lines:
                        if self.promptRegex.match(line):
                            promptMatch = promptMatch + 1
                            if promptMatch == maxMatch:
                                #Prompt detected exit
                                coutstr=""
                                return

    def _disablePaging(self):
        """disables paging on the console to prevent the need to interact with a pagnated set of output"""
        self._runSilentCommand("set console page 0",2)

    def _enablePaging(self):
        """disables paging on the console to prevent the need to interact with a pagnated set of output"""
        self._runSilentCommand("set console page 20",1)

    def _clear_admin_sessions(self):
        """disables paging on the console to prevent the need to interact with a pagnated set of output"""
        self._runSilentCommand("clear admin all",1)

    def _exit_session(self,save=False):
        """Exit the ssh session. Optionally save config."""
        #sleep to slow input to the device
        time.sleep(0.2)
        self.chan.send("exit\n")
        coutstr=""
        result=""
        promptMatch = 0
        maxMatch = 1
        configModMatch = ".*Configuration modified\, save\? \[y\]\/n.*"
        configModMatchRe = re.compile(configModMatch)
        while True:
            #Gather the output from the command until the prompt is detected
            if self.chan.recv_ready():
                coutstr = self.chan.recv(1024)
                result += coutstr
                if len(coutstr) < 1024:
                    lines = result.splitlines()
                    for line in lines:
                        if self.promptRegex.match(line):
                            promptMatch = promptMatch + 1
                            if promptMatch == maxMatch:
                                #Prompt detected exit
                                return
                        elif configModMatchRe.match(line):
                            if save == True:
                                self.chan.send("y")
                                return
                            else:
                                self.chan.send("n")
                                return

    def runCommand(self,command):
        """Run a specified command against the device, returns the output of the command"""
        #sleep to slow input to the device
        time.sleep(0.2)
        self.chan.send(command + "\n")
        coutstr=""
        result=""
        finalOutput = ""
        promptMatch = 0
        lineCount = 0
        while True:
            #Gather the output from the command until the prompt is detected
            if self.chan.recv_ready():
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
                            pass
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
            #Gather the output from the command until the hostname is detected
            if hostnameMatchRe.match(line):
                result = hostnameMatchRe.match(line)
                self.systemFacts["hostname"] = result.group(1)


    def checkPlatform(self):
        """Determine the local platform type"""

        # Example Match Product Name: NetScreen-5400-III
        systemMatch = "Product Name: ([\w\W]+)"
        systemMatchRe = re.compile(systemMatch)

        # Example Match Serial Number: 0047122010000025, Control Number: 00000000
        serialNumberMatch = "Serial Number: ([\w]+), Control Number: ([\w]+)"
        serialNumberMatchRe = re.compile(serialNumberMatch)

        # Example Match Software Version: 6.2.0r9-cu4.0, Type: Firewall+VPN
        softwareVersionMatch = "Software Version: ([\w\W]+), Type: ([\w\W]+)"
        softwareVersionMatchRe = re.compile(softwareVersionMatch)

        output = self.runCommand("get system")
        splitLines = output.splitlines()
        for line in splitLines:
            #Gather the output from the command until the correct facts are detected
            if systemMatchRe.match(line):
                #Match the product name
                result = systemMatchRe.match(line)
                self.systemFacts["product"] = result.group(1)
            elif serialNumberMatchRe.match(line):
                #Match the serial and control numbers
                result = serialNumberMatchRe.match(line)
                self.systemFacts["serialNumber"] = result.group(1)
                self.systemFacts["controlNumber"] = result.group(2)
            elif softwareVersionMatchRe.match(line):
                #Match the version and type of product
                result = softwareVersionMatchRe.match(line)
                self.systemFacts["version"] = result.group(1)
                self.systemFacts["type"] = result.group(2)

    def _getAsicCounter(self,asicid,qmuid):
        """Get the counters from the specified asic"""
        if self.systemFacts["product"] == "":
            #print "Product facts not gathered"
            pass
        #ISG Match
        elif self.systemFacts["product"] == ASICList["NetScreen-2000"]["productString"] or self.systemFacts["product"] == ASICList["NetScreen-ISG1000"]["productString"]:
            output = self.runCommand("get asic engine qmu pktcnt %s" % (qmuid))
            return output
        #NS5400 Match
        elif self.systemFacts["product"] == ASICList["NetScreen-5400-II"]["productString"] or self.systemFacts["product"] == ASICList["NetScreen-5400-III"]["productString"]:
            output = self.runCommand("get asic %s engine qmu pktcnt %s" % (asicid,qmuid))
            return output
        #NS52000 Match
        elif self.systemFacts["product"] == ASICList["NetScreen-5200-II"]["productString"] or self.systemFacts["product"] == ASICList["NetScreen-5200"]["productString"]:
            output = self.runCommand("get asic %s engine qmu pktcnt %s" % (asicid,qmuid))
            return output

    def _compileAsicDict(self,endValues,asicid,queueList,runid,lines):
        """parse asic data"""
        for queue in queueList:
            if queue in endValues[asicid]:
                #queue initilized already
                pass
            else:
                #Create dict structre for values
                endValues[asicid][queue] = {}

            if runid in endValues[asicid][queue]:
                #runid initalized already
                pass
            else:
                endValues[asicid][queue][runid] = ""

            queueRE = re.compile("pktcnt\[%s\s+\]\s=\s(0x\d{8})\s+(\d*)" % (queue))
            for line in lines:
                #Gather values for the output
                if queueRE.match(line):
                    matchResult = queueRE.match(line)
                    endValues[asicid][queue][runid] = matchResult.group(1)

            return endValues

    def getAllAsicCounters(self,verbose):
        """Get all counters from the platform"""
        #itterate through the asics and the counters on the platform
        endValues = dict()
        verboseOutput = []
        if self.systemFacts["product"] in ASICList:
            asic_list = ASICList[self.systemFacts["product"]]["asic_list"]
            qmu_list = ASICList[self.systemFacts["product"]]["qmu_list"]
            runid = "0"
            for asic in asic_list:
                endValues[asic] = {}
                for qmu in qmu_list:
                    #Get the inital asic counters to initialize the buffer, ignore output
                    self._getAsicCounter(asic,qmu)
                    #Get the ASIC counters and save the output
                    output = self._getAsicCounter(asic,qmu)
                    lines = output.split("\n")
                    if verbose:
                        verboseOutput.extend(lines)
                    queueList = BUFFERList[str(qmu)]
                    endValues = self._compileAsicDict(endValues,asic,queueList,runid,lines)
            runid = "1"
            for asic in asic_list:
                for qmu in qmu_list:
                    self._getAsicCounter(asic,qmu)
                    output = self._getAsicCounter(asic,qmu)
                    lines = output.split("\n")
                    if verbose:
                        verboseOutput.extend(lines)
                    queueList = BUFFERList[str(qmu)]
                    endValues = self._compileAsicDict(endValues,asic,queueList,runid,lines)
            self.asicCounters = endValues
        return endValues, verboseOutput

    def compareAsicCounters(self):
        """compare the two asic values"""
        finalOutput = []
        if len(self.asicCounters) > 0:
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
                                finalOutput.append("Packet loss of %d packet(s) detected in ASIC %s witin queue %s on host %s" % (asicDiff,asic,queue.rjust(6),self.systemFacts["hostname"]))
                        else:
                            if self.output:
                                finalOutput.append("No packet loss detected in ASIC %s witin queue %s on host %s" % (asic,queue.rjust(6),self.systemFacts["hostname"]))
        return finalOutput

    def disconnect(self):
        """Disconnect from the device"""
        self._enablePaging()
        self._exit_session()
        self.chan.close()
        self.transport.close()
        self.socket.close()

#Main part of program

#Create argument parser
parser = argparse.ArgumentParser(description="Gather options from the user")
parser.add_argument("--output", dest="output", action="store_true",help="Specify if you want to print output to standard out. Defaults to printing output.")
parser.add_argument("--no-output", dest="output", action="store_false",help="Specify if you do not want to print output to standard out.")
parser.add_argument("--clear-session", dest="clear_session", action="store_true",help="Clears all other admin sessions. Ensure the successful completion of the script.")
parser.set_defaults(clear_session=False)
parser.set_defaults(output=True)
parser.add_argument("--log",dest="log",default="",help="Specify the file name where to save the output to.")
parser.add_argument("--log-level",dest="logLevel",default="0",metavar="LOGLEVEL",help="Specify the verbosity of logging. Default 0 provides basic logging. Setting log level to 1 provides max output.")
parser.add_argument("--csv", dest="hostCSVFile", default="",metavar="CSVFile",help="Specify the CSV file to read hosts from.")
parser.add_argument("--host", dest="host", default="",metavar="HOST",help="Specify single host to connect to. Can not be used with --csv.")
parser.add_argument("--username", dest="username", default="netscreen",metavar="USERNAME",help="Specify the default username to use when not specified within the csv.")
parser.add_argument("--password", dest="password", default="netscreen",metavar="PASSWORD",help="Specify the default password to use when not specified within the csv.")
parser.add_argument("--password-secure", dest="passwordSecure", action="store_true", help="Be prompted for the the default password.")
args = parser.parse_args()

userPassword = ""
verboseLogging = False

#check for secure password
if args.passwordSecure == True:
    password = getpass.getpass()
    userPassword = password
else:
    userPassword = args.password

#check for logging level
if args.logLevel == "0":
    verboseLogging = False
elif args.logLevel == "1":
    verboseLogging = True

logger = OutputLogger(args.output,args.log)
logger.addPrefix(socket.gethostname())

if args.hostCSVFile != "": #check if singular hosts are specified

    hp = HostParser(args.hostCSVFile)
    if args.output:
        if len(hp.hostList) > 1:
            logger.log("Found %s hosts in %s CSV file. Starting stats gathering." % (len(hp.hostList),args.hostCSVFile),True)
        elif len(hp.hostList) == 0:
            logger.log("Found %s hosts in %s CSV file. No hosts to gather stats from." % (len(hp.hostList),args.hostCSVFile),True)
        else:
            logger.log("Found %s hosts in %s CSV file. Starting stats gathering." % (len(hp.hostList),args.hostCSVFile),True)

    for item in hp.getHosts():
        if item["username"] == "":
            item["username"] = args.username

        if item["password"] == "":
            item["password"] = userPassword

        #Add local hostname to the log

        agent = NetScreenAgent(item["host"],item["username"],item["password"],args.output,args.clear_session)
        if args.output:
            logger.log("======================================================================",True)
            logger.log("Connecting to host %s" % (item["host"]),True)
        try:
            agent.connect()
            agent.getSystemFacts()
            if agent.systemFacts["product"] != "":
                if args.output:
                    logger.log("Successfully connected to host %s" % (item["host"]),True)
                    logger.log("Host: %s Product: %s Serial Number: %s" % (agent.systemFacts["hostname"],agent.systemFacts["product"],agent.systemFacts["serialNumber"]),True)
                endValues, verboseOutput = agent.getAllAsicCounters(verboseLogging)
                if len(verboseOutput) > 0:
                    for line in verboseOutput:
                        logger.log(line,True)

                agent.disconnect()
                counters = agent.compareAsicCounters()
                for line in counters:
                    logger.log(line,True)
                logger.log("======================================================================\n",True)
            else:
                logger.log("Failed to fetch system facts about host: %s" % (item["host"]),True)
        except Exception, e:
            logger.log(str(e))
elif args.host != "":
    agent = NetScreenAgent(args.host,args.username,userPassword,args.output,args.clear_session)
    if args.output:
        logger.log("======================================================================",True)
        logger.log("Connecting to host %s" % (args.host),True)
    try:
        agent.connect()
        agent.getSystemFacts()
        if agent.systemFacts["product"] != "":
            if args.output:
                logger.log("Successfully connected to host %s" % (args.host),True)
                logger.log("Host: %s Product: %s Serial Number: %s" % (agent.systemFacts["hostname"],agent.systemFacts["product"],agent.systemFacts["serialNumber"]),True)

            endValues, verboseOutput = agent.getAllAsicCounters(verboseLogging)
            if len(verboseOutput) > 0:
                for line in verboseOutput:
                    logger.log(line,True)

            agent.disconnect()

            counters = agent.compareAsicCounters()
            for line in counters:
                logger.log(line,True)
            logger.log("======================================================================\n",True)
        else:
            logger.log("Failed to fetch system facts about host: %s" % (args.host),True)
    except Exception, e:
        logger.log(str(e))
else:
    parser.print_help()
