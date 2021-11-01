import socket
import time
import datetime
import threading
 
class Node():
    port = -1
    executing_cs = False
    requesting_cs = False
    waiting_reply_q = None
    host = "?"
    s_listener = None
    keep_listeing = True
    node_name = "?"
    connectedNodeList=list()
    defferedRequest=None
    logical_clock = None
    logFile = None
    ##
    def __init__(self,port,node_name):
        self.port = port
        self.host = socket.gethostname()
        self.node_name = node_name
        self.logical_clock = 0
        self.defferedRequest = list()
        self.connectedNodeList = list()
        self.keep_listeing = True
        self.waiting_reply_q = list()
        self.requesting_cs = False
        self.executing_cs = False
        self.logFile=open(f'{self.node_name}_{self.port}.log','w')

    ##
    def start(self):
        listenerThread = threading.Thread(target=self._start_accepting_msg)
        listenerThread.start()
        self._logger(f'Listening started on this node')
    ##
    def _start_accepting_msg(self):
        self.s_listener = socket.socket()
        self.s_listener.bind((self.host,self.port))
        self.s_listener.listen()
        while self.keep_listeing:
            connection,addr=self.s_listener.accept()
            received_message = connection.recv(2048).decode()
            if(len(received_message) > 0 ):
                self._msgHandler(received_message)
            connection.close()
        self.close()
    ##
    def close(self):
        self.s_listener.close()
   
    ##
    def _getHostName(self):
        return self.host
    ##
    def send(self,target_port,message):
        if('REPLY' in message):
            self._logger(f'Sending "{message}" to {target_port}')
        send_socket = socket.socket()
        send_socket.connect((self._getHostName(),target_port))
        send_socket.send(message.encode('ascii'))
        send_socket.close()
    ##
    def _msgHandler(self,message):
        ##Handling stopping of node using STOP message
        if('STOP_NODE' in message):
            mport=int(message.split(',')[1])
            if(mport == self.port):
                self.keep_listeing = False
                self._logger('Stopping node now')
        if('REQUEST' in message):
            csRequestHandlerThread = threading.Thread(target=self._handleCSRequest,args=(message,))
            csRequestHandlerThread.start()
        if('REPLY' in message):
            csReplyHandlerThread = threading.Thread(target=self._handleCSReply,args=(message,))
            csReplyHandlerThread.start()
 
    ##
    def _executeCS(self):
        self.executing_cs=True
        self._logger('Executing CS')
        time.sleep(10)
        self._logger('Critical section execution finished')
        self.executing_cs=False
        if len(self.defferedRequest) > 0:
            self._logger('processing deffered queue')
            self._processDeferredQueue()
       
    def _processDeferredQueue(self):
        self._logger(f'Current deferred request queue is {self.defferedRequest}')
        for message in self.defferedRequest:
            sourcePort = int(message.split(',')[1])
            self._logger(f'Sending deffered REPLY to {sourcePort}')
            self.send(sourcePort,f'REPLY,{self.port}')  
        self.requesting_cs = False
    ##
    def _handleCSReply(self,message):
        sourcePort=int(message.split(',')[1])
        self._logger(f'Received REPLY node {sourcePort}')
        if sourcePort in self.waiting_reply_q:
            self._logger(f'Removing {sourcePort} from reply waiting queue')
            self.waiting_reply_q.remove(sourcePort)
        if len(self.waiting_reply_q) == 0:
            csExecutionThread = threading.Thread(target=self._executeCS)
            csExecutionThread.start()
        else:
            self._logger(f'Awaiting reply from nodes {self.waiting_reply_q}')
 
    ##
    def _handleCSRequest(self,message):
        self._incrementLogicalClock()
        sourcePort=int(message.split(',')[1])
        sourceTimestamp=int(message.split(',')[2])
        self._logger(f'Received request for CS execution from node {sourcePort} TS = {sourceTimestamp}')
       
        condition1=False
        condition2=False
        #Condition 1 - If requesting or executing CS already ?
        condition1 = self.requesting_cs
        #Condition 2 - the receiving process has a lower priority (usually this means having a later timestamp)
        if(self.requesting_cs):
            if(self.logical_clock>sourceTimestamp):
                condition2 = True
            else:
                if(self.logical_clock == sourceTimestamp):
                    if(self.port < sourcePort):
                        condition2 = True
        if((condition1 and condition2) or self.executing_cs):
            self._logger(f'Deffering request {message}')
            self.defferedRequest.append(message)
        else:
            self.send(sourcePort,f'REPLY,{self.port}')
    ##
    def stop(self):
        self.keep_listeing = False
        self.host = socket.gethostname()
        self.send(self.port,f'STOP_NODE,{self.port}')
   
    ##
    def setConnectedNodes(self, nodeList):
        self.connectedNodeList=nodeList.copy()
   
    def _requesting_critical_section(self,defer_cs_request_time):
        if(self.requesting_cs):
            self._logger('Already requested CS and awaiting execution completion')
            return
        self.requesting_cs = True
        if(defer_cs_request_time > 0):
            self._logger(f'Deffering CS request by {defer_cs_request_time} seconds')
            time.sleep(defer_cs_request_time)
        self._incrementLogicalClock()
        for targetPort in self.connectedNodeList:
            if(targetPort != self.port):
                self.waiting_reply_q.append(targetPort)
 
        for targetPort in self.connectedNodeList:
            if(targetPort != self.port):
                request_message = f'REQUEST,{self.port},{self.logical_clock}'
                self._logger(f'Sending CS request to node {targetPort} - "{request_message}"')
                self.send(targetPort,request_message)
 
    def requestCS(self,defer_cs_request_time=0):
        requestCSThread = threading.Thread(target=self._requesting_critical_section,args=(defer_cs_request_time,))
        requestCSThread.start()
    ##
    def _incrementLogicalClock(self):
        self.logical_clock += 1
 
    ##
    def _logger(self,message):
        timestamp =  datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        logsuffix = f'{self.node_name} {self.port} - {timestamp} # '
        self.logFile.writelines(f'{logsuffix} {message}\n')
        self.logFile.flush()
        print(f'{logsuffix} {message}')