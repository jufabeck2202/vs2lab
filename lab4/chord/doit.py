""" 
Chord Application
- defines a DummyChordClient implementation
- sets up a ring of chord_node instances
- Starts up a DummyChordClient
- nodes and client run in separate processes
- multiprocessing should work on unix and windows
"""

import logging
import sys
import time
from multiprocessing import Process
import random
import math

import chordnode as chord_node
import constChord

from context import lab_channel, lab_logging

lab_logging.setup(stream_level=logging.INFO)

if __name__ == "__main__":  # if script is started from command line
    m = 6  # Number of bits for linear names
    n = 16  # Number of nodes in the chord ring

    # Check for command line parameters m, n.
    if len(sys.argv) > 2:
        m = int(sys.argv[1]) #number of bits
        n = int(sys.argv[2]) #number of nods

    # Create a communication channel.,.  ö,
    chan = lab_channel.Channel(n_bits=m)
    chan.channel.flushall()

    #klasse
    class DummyChordClient:
        """A dummy client template with the channel boilerplate"""

        def __init__(self, channel):
            self.channel = channel
            self.node_id = channel.join('client')

        def run(self):
            self.channel.bind(self.node_id)
            destination = [random.choice(list(self.channel.channel.smembers('node'))).decode()]
            key = random.randint(0,math.pow(2,m)-1)
            print("Sending Request to:",destination, " for Key:",key)
            chan.send_to(destination,(constChord.LOOKUP_REQ,key))
            while True:
                message = self.channel.receive_from_any()
                sender: str = message[0]  # Identify the sender
                request = message[1]  # And the actual request
                if request[0] == constChord.LOOKUP_REP:
                    print("#########################################")
                    print("Node ",request[1]," is responsible for ",key)
                    chan.send_to({i.decode() for i in list(self.channel.channel.smembers('node'))},constChord.STOP)
                    break

    # Init n chord nodes and a client
    nodes = [chord_node.ChordNode(chan) for node in range(n)]
    client = DummyChordClient(chan)

    # start n chord nodes in separate processes
    children = []
    for i in range(n):
        nodeproc = Process(
            target=lambda o: o.run(),
            name="ChordNode-" + str(i),
            args=(nodes[i],))
        children.append(nodeproc)
        nodeproc.start()
        time.sleep(0.25)

    clientproc = Process(
        target=lambda o: o.run(),
        name="ChordClient",
        args=(client,))

    # start client and wait for it to finish
    clientproc.start()
    clientproc.join()

    # wait for nodes to finish
    for nodeproc in children:
        nodeproc.join()
