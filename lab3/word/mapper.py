# Task worker
# Connects PULL socket to tcp://localhost:5557
# Collects workloads from ventilator via that socket
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import constPR
context = zmq.Context()


me = str(sys.argv[1])
port = ""

if me == "1":
    port = constPR.MAPPER1
elif me == "2":
    port = constPR.MAPPER2
elif me == "3":
    port = constPR.MAPPER3

print("connected to port "+ port)
# Socket to the splitter

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://" + constPR.HOST + ":" + port)


# Reducer to send messages
r1 = context.socket(zmq.PUSH)
r1.connect("tcp://" + constPR.HOST + ":" + constPR.REDUCE1)
r2 = context.socket(zmq.PUSH)
r2.connect("tcp://" + constPR.HOST + ":" + constPR.REDUCE2)

# Process tasks forever
print("Mapper Started")
firstHalf = []
while True:
    s = receiver.recv_string()
    #send half the words to 1 the rest to 2
    for word in s.split():
        if 97 <= ord(word[0][0]) < 110:
            r1.send_string(word)
        else:
            r2.send_string(word)


print("finished working")