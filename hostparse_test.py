import nsautomate
import exceptions
import sys

hp = nsautomate.HostParser("./test-devices.csv")
print hp.hostList

for item in hp.getHosts():
    agent = nsautomate.NetScreenAgent(item["host"],item["username"],item["password"],True)
    agent.connect()
    agent.getSystemFacts()
    if agent.systemFacts["product"] != "":
        print agent.systemFacts
        agent.getAllAsicCounters()
        agent.disconnect()
        agent.compareAsicCounters()
    else:
        print "Failed to fetch system facts about host: %s" % (item["host"])

"""
for item in hp.getHosts():
    agent = nsautomate.NetScreenAgent(item["host"],item["username"],item["password"],True)
    agent.connect()
    agent.getSystemFacts()
    print agent.systemFacts
    agent.getAllAsicCounters()
    agent.disconnect()
    try:
        agent.connect()
        agent.getSystemFacts()
        print agent.systemFacts
        agent.getAllAsicCounters()
        agent.disconnect()
    except:
        print sys.exc_info()
"""
