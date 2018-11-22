# Task sink
# Binds PULL socket to tcp://localhost:5558
# Collects results from workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import pprint
import constPR
pp = pprint.PrettyPrinter(indent=4)
context = zmq.Context()


me = str(sys.argv[1])
port = ""

if me == "1":
    port = constPR.REDUCE1
elif me == "2":
    port = constPR.REDUCE2


print("connected to port "+ port)

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://" + constPR.HOST + ":" + port)
map = {}
while True:
    s = receiver.recv_string();
    if s not in map:
        map[s] = 1
    else:
        map[s] += 1
    print("###########################")
    pp.pprint(map)

