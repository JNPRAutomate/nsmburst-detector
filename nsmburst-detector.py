"""
Microburst detection tool for ASIC-based NetScreen platforms
"""
import socket
import paramiko
import re

ASICList = { "ns5400": {"asic_list": [0,1,2,3,4,5], "qmu_list":[1,2,4,6,7,9]}, "isg1000": { "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }, "isg2000": { "asic_list": [0], "qmu_list":[1,2,4,6,7,9] }}

class NetScreenAgent:
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
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.remoteHost,22))
        self.transport = paramiko.Transport(self.socket)
        self.transport.start_client()
        self.transport.auth_password(username=self.username,password=self.password)
        self.chan = self.transport.open_channel("session")
        #self.chan.get_pty(term='vt100', width=80, height=24)
        #self.chan.set_combine_stderr(True)
        #self.chan.setblocking(blocking=1)
        #self.chan.settimeout(timeout=5)
        self.chan.invoke_shell()

        #self.sshClient = paramiko.SSHClient()
        #self.sshClient.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        #self.sshClient.connect(self.remoteHost,username=self.username,password=self.password,allow_agent=False,compress=False,look_for_keys=False)

    def runCommand(self,command):
        """Run a specified command"""
        bytesSent = self.chan.send(command)
        print "Sent " + str(bytesSent)
        coutstr=""
        result=""
        while not self.chan.closed:
            coutstr = self.chan.recv(1024)
            result += coutstr
            print len(coutstr)
            if len(coutstr) < 1024:
                break
        print result

        #stdin, stdout, stderr = self.sshClient.exec_command(command)
        #print stdout.read()
        #print stderr.read()

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
        self.sshClient.exec_command("get asic %s engine qmu pktcnt %s" % (asicid,qmuid))

    def disconnect(self):
        """Disconnect from the device"""
        self.chan.close()
        self.transport.close()


agent = NetScreenAgent("10.0.1.222","netscreen","netscreen",True)
agent.connect()
agent.runCommand("get config")

agent.disconnect()
