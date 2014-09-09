"""
Microburst detection tool for ASIC-based NetScreen platforms
"""
import paramiko
import re

foo = {}

ASICList = { "ns5400": {"asic_list": [0,1,2,3,4,5], "qmu_list":[1,2,4,6,7,9]}, "isg1000": { "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }, "isg2000": { "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }}

class MburstAgent:
    def __init__(self,hostname,username,password,output):
        """Initalize the object with the correct hostname,username, and password"""
        self.remoteHost = hostname
        self.username = username
        self.password = password
        self.platform = ""
        if output:
            self.output = output
        else:
            self.output = false

    def connect(self):
        """Create a connection to the remote device"""
        self.sshClient = paramiko.SSHClient()
        self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshClient.connect(self.remoteHost,username=self.username,password=self.password,look_for_keys=0)

    def runCommand(self,command):
        """Run a specified command"""
        stdin, stdout, stderr = self.sshClient.exec_command(command)
        print stdout.read()
        print stderr.read()

    def checkPlatform(self):
        """Determine the local platform type"""
        # Product Name: NetScreen-5400-III
        systemMatch = "Product Name: ([\w\W]+)"
        # Serial Number: 0047122010000025, Control Number: 00000000
        serialNumberMatch = "Serial Number: ([\d]+), Control Number: ([\d]+)"
        #Software Version: 6.2.0r9-cu4.0, Type: Firewall+VPN
        softwareVersionMatch = "Software Version: ([\w\W]+), Type: ([\w\W]+)"
        systemMatchRe = re.compile(systemMatch)

        stdin, stdout, stderr = self.sshClient.exec_command("get system")
        outputLines = stdout.splitlines()
        for line in outputLines:
            print line

    def getAsicCoutners(self,asicid,qmuid):
        """Get the counters from the specified asic"""
        self.sshClient.exec_command("set asic %s engine qmu pktcnt %s" % (asicid,qmuid))

    def disconnect(self):
        """Disconnect from the device"""
        self.sshClient.close()


agent = MburstAgent("172.16.244.171","vagrant","vagrant",True)
agent.connect()
agent.runCommand("ls -la")
agent.disconnect()
