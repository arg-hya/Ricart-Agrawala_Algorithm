OS Dependency ::
--------------------
No OS dependency

PYTHON VERSION ::
-----------------------
python 3.7.0 or greater

INPUT ::
----------
Input to code will be given through file InputData.csv (sample file exists)
Format of input :: ProcessName,PortName

For Ex:
proc1,50001
proc2,50002

Above config can be used to define two node cluster

Start Cluster and Request Critical Section ::
----------------------------------------------
Cluster can be started as below 
1. Config cluster or number of processes using file "InputData.csv"
2. In nodeStart.py file - Critical section can be reqested using including code line "nodeProcesses[<index>].requestCS(<sleeping time before starting node CS request>)"
3. Start cluster using command "python3 nodeStart.py"

Stop Cluster ::
-----------------
Cluster can be stopped using command "python3 nodeStop.py"

Logs ::
-----------
Each process will create a new log file with name "<processname>_<port>.log"
processname,port are defined in config file

Assumptions ::
---------------
1. Critical section for each process will be executed for 10 seconds
2. There should be different defer time for each process for critical section request. If two process executes at the same time then there are chances of deadlock which is not handled in this code yet.
3. Cluster will keep running once all the Critical section executed successfully(Just to mimic actual sites which keep running)



