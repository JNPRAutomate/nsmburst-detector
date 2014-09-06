"""
Microburst detection tool for ASIC-based NetScreen platforms
"""
import pexpect
import paramiko

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

    def checkPlatform(self):
        """Determine the local platform type"""

    def getAsicCoutners(self,asicid):
        """Get the counters from the specified asic"""

    def
