import node
config_file = open('InputData.csv','r')
config_data=config_file.readlines()
for config_item in config_data:
    if '#' in config_item:
        pass
    else:
        nodename,port=config_item.strip().split(',')
        nodeProc = node.Node(node_name=nodename,port=int(port))
        nodeProc.stop()
