import zmq
import random
import time
import re
import sys
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


print("Splitter Ready!")


# Initialize random number generator
random.seed()

# open file, read lines
with open("words.txt") as f:
    content = f.readlines()
    content = [x.strip() for x in content]

i = 0
sendTo1 =0
sendTo2 = 0
sendTo3 = 0
print("Press Enter when the workers are ready: ")
while True:
    _ = raw_input()
    for line in content:
        #remove space
        #send to mappers
        line = line.lower()
        line = re.sub('[!@#$:,.„“,?]', '', line)
        if i%3 == 0:
            m3.send_string(line)
            sendTo3 +=1
        elif i%3 == 1:
            m1.send_string(line)
            sendTo1+=1
        elif i%3 == 2:
            m2.send_string(line)
            sendTo2+=1
        sys.stdout.write("Send to M1: %d | Send to M2: %d | Send to M3: %d  \r" % (sendTo1, sendTo2,sendTo3))
        sys.stdout.flush()
        i += 1



# Give 0MQ time to deliver
time.sleep(1)