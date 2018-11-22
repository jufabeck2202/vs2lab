# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import zmq
import random
import time
import re
import constPR

try:
    raw_input
except NameError:
    # Python 3
    raw_input = input

context = zmq.Context()

# MAPPERS
m1 = context.socket(zmq.PUSH)
m1.connect("tcp://" + constPR.HOST + ":" + constPR.MAPPER1)
m2 = context.socket(zmq.PUSH)
m2.connect("tcp://" + constPR.HOST + ":" + constPR.MAPPER2)
m3 = context.socket(zmq.PUSH)
m3.connect("tcp://" + constPR.HOST + ":" + constPR.MAPPER3)


print("Splitter is ready!")
print("Press Enter when the workers are ready: ")
_ = raw_input()
print("Sending tasks to workers…")


# Initialize random number generator
random.seed()

# open file, read lines
with open("words.txt") as f:
    content = f.readlines()
    content = [x.strip() for x in content]

i = 0
for line in content:
    #remove space
    #send to mappers
    line = line.lower()
    if i%3 == 0:
        print("send to 3:")
        m3.send_string(line)
    elif i%3 == 1:
        print("send to 1:")
        m1.send_string(line)
    elif i%3 == 2:
        print("send to 2:")
        m2.send_string(line)
    i += 1



# Give 0MQ time to deliver
time.sleep(1)