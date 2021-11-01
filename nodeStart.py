import node
import time
config_file = open('InputData.csv','r')
nodeListDict={}
config_data=config_file.readlines()
config_file.close()
for config_item in config_data:
    if '#' in config_item:
        pass
    else:
        nodename,port=config_item.strip().split(',')
        nodeListDict[nodename] = int(port)
connectedNodePortList = list(nodeListDict.values())
nodeProcesses=list()
nodeProcesses = [node.Node(node_name=node_name,port=nodeListDict[node_name]) for node_name in list(nodeListDict.keys())]

for node in nodeProcesses:
    node.setConnectedNodes(connectedNodePortList)
    node.start()

nodeProcesses[0].requestCS(1)
nodeProcesses[1].requestCS(2)
nodeProcesses[2].requestCS(3)
nodeProcesses[3].requestCS(4)
nodeProcesses[4].requestCS(5)