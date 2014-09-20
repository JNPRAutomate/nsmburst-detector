import nsautomate

username = raw_input("Please enter the default username: ")
password = raw_input("Please enter the default password: ")
agent = nsautomate.NetScreenAgent("172.22.152.24",username,password,True)
#agent = NetScreenAgent("10.0.1.222","netscreen","netscreen",True)
agent.connect()
agent.getSystemFacts()
print agent.systemFacts
agent.getAsicCountners("","")
agent.disconnect()
