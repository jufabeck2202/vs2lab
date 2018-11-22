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

# Socket to the splitter
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://" + constPR.HOST + ":" + port)
print("Mapper "+me+" connected to port "+ port)


# Reducer to send messages
r1 = context.socket(zmq.PUSH)
r1.connect("tcp://" + constPR.HOST + ":" + constPR.REDUCE1)
r2 = context.socket(zmq.PUSH)
r2.connect("tcp://" + constPR.HOST + ":" + constPR.REDUCE2)

# Process tasks forever
print("Mapper "+ me + "started, waiting for data")
sendTo1 = 0
sendTo2 = 0
while True:
    s = receiver.recv_string()
    #send half the words to 1 the rest to 2
    for word in s.split():
        if 97 <= ord(word[0][0]) < 109:
            r1.send_string(word)
            sendTo1+=1
        else:
            r2.send_string(word)
            sendTo2+=1
        sys.stdout.write("Send to Reducer 1: %d | Send to Reducer 2: %d   \r" % (sendTo1, sendTo2))
        sys.stdout.flush()