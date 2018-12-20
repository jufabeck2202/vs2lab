import logging
import random
import time

import constMutex


class Process:
    """
    Implements access management to a critical section (CS) via fully
    distributed mutual exclusion (MUTEX).

    Processes broadcast messages (ENTER, ALLOW, RELEASE) timestamped with
    logical (lamport) clocks. All messages are stored in local queues sorted by
    logical clock time.

    A process broadcasts an ENTER request if it wants to enter the CS. A process
    that doesn't want to ENTER replies with an ALLOW broadcast. A process that
    wants to ENTER and receives another ENTER request replies with an ALLOW
    broadcast (which is then later intime than its own ENTER request).

    A process enters the CS if a) its ENTER message is first in the queue (it is
    the oldest pending message) AND b) all other processes have send messages
    that are younger (either ENTER or ALLOW). Release requests purge
    corresponding ENTER requests from the top of the local queues.

    Message Format:

    <Message>: (Timestamp, Process_ID, <Request_Type>)

    <Request Type>: ENTER | ALLOW  | RELEASE

    """

    def __init__(self, chan):
        self.channel = chan  # Create ref to actual channel
        self.process_id = self.channel.join('proc')  # Find out who you are
        self.all_processes: list = []  # All procs in the proc group
        self.other_processes: list = []  # Needed to multicast to others
        self.queue = []  # The request queue list
        self.clock = 0  # The current logical clock
        self.logger = logging.getLogger("vs2lab.lab5.mutex.process.Process")

    def __cleanup_queue(self):
        if len(self.queue) > 0:
            self.queue.sort()
            # There should never be old ALLOW messages at the head of the queue
            while self.queue[0][2] == constMutex.ALLOW:
                del (self.queue[0])
                if len(self.queue) == 0:
                    break

    def __request_to_enter(self):
        self.clock = self.clock + 1  # Increment clock value
        # Append request to queue
        self.queue.append((self.clock, self.process_id, constMutex.ENTER))
        self.__cleanup_queue()  # Sort the queue
        self.channel.send_to(self.other_processes, (self.clock,
                             self.process_id, constMutex.ENTER))  # Send request

    def __allow_to_enter(self, requester):
        self.clock = self.clock + 1  # Increment clock value
        self.channel.send_to(
            [requester], (self.clock, self.process_id, constMutex.ALLOW))  # Permit other

    def __release(self):
        # need to be first in queue to issue a release
        assert self.queue[0][1] == self.process_id
        # construct new queue from later ENTER requests (removing all ALLOWS)
        tmp = [r for r in self.queue[1:] if r[2] == constMutex.ENTER]
        self.queue = tmp  # and copy to new queue
        self.clock = self.clock + 1  # Increment clock value
        self.channel.send_to(self.other_processes, (self.clock,
                             self.process_id, constMutex.RELEASE))  # Release

    def __allowed_to_enter(self):
        processes_with_later_message = set(
            [req[1] for req in self.queue[1:]])  # See who has sent a message
        # Access granted if this process is first in queue and all others have answered (logically) later
        return self.queue[0][1] == self.process_id and len(self.other_processes) == len(processes_with_later_message)

    def __receive(self):
        msg = self.channel.receive_from(self.other_processes,5)
        if msg is None:
            print()
            print("Timeout detected in {} with Queue {} \n Sending Ping".format(self.process_id, self.queue))

            self.channel.send_to(self.other_processes,constMutex.PING)
            received_pongs = []
            while len(received_pongs) is not len(self.other_processes):
                msg = self.channel.receive_from(self.other_processes, 5)
                if msg is None:
                    break
                received_pongs.append(msg[0])
            offline_proc = list(set(self.other_processes) - set(received_pongs))[0]
            for i in self.queue:
                if int(i[1]) is int(offline_proc):
                    self.queue.remove(i)
            self.other_processes.remove(offline_proc)
            self.all_processes.remove(offline_proc)
            #make sure process id is in postion [0]
            self.all_processes.remove(str(self.process_id))
            self.all_processes.insert(0, str(self.process_id))
            self.clock = self.clock + 1
            print("{} Removed Pro {}, own Queue {}".format(self.process_id,offline_proc,self.queue))

            self.__cleanup_queue()  # Finally sort and cleanup the queue
            return

        msgFrom = msg[0]
        msg = msg[1]
        self.clock = max(self.clock, msg[0])  # Adjust clock value...
        self.clock = self.clock + 1  # ...and increment
        self.logger.debug("Process {} received {} from {}.".format(
            self.process_id,
            "ENTER" if msg[2] == constMutex.ENTER
                else "ALLOW" if msg[2] == constMutex.ALLOW
                    else "RELEASE", msg[1]))

        if msg[2] == constMutex.ENTER:
            self.queue.append(msg)  # Append an ENTER request
            # and unconditionally allow (don't want to access CS oneself)
            self.__allow_to_enter(msg[1])
        elif msg[2] == constMutex.ALLOW:
            self.queue.append(msg)  # Append an ALLOW
        elif msg[2] == constMutex.PING:
            self.channel.send_to(msgFrom, "pong")
        elif msg[2] == constMutex.RELEASE:
            # assure release requester indeed has access (his ENTER is first in queue)
            assert self.queue[0][1] == msg[1] and self.queue[0][2] == constMutex.ENTER
            del (self.queue[0])  # Just remove first message

        self.__cleanup_queue()  # Finally sort and cleanup the queue
        self.logger.debug("Process {} cleaned local queue {}.".format(
            self.process_id, self.queue))

    def enter(self):
        self.channel.bind(self.process_id)
        self.logger.debug("Process {} joined channel.".format(self.process_id))

        self.all_processes = list(self.channel.subgroup('proc'))
        self.all_processes.sort()

        self.other_processes = list(self.channel.subgroup('proc'))
        self.other_processes.remove(self.process_id)

    def run(self):
        while True:
            # Try to enter critical section if this process is first in list.
            # Occasionally try to enter if not first in list.
            # Only do that if there are any other processes left.
            #print(self.all_processes, " ", self.process_id != self.all_processes[-1], " ID",self.process_id)
            #print("Process id: {} self.all_processes: {}".format(self.process_id,self.all_processes))
            if self.process_id != self.all_processes[-1] and \
                    (self.process_id == self.all_processes[0] or \
                        random.choice([True, False])):
                self.logger.debug("Process {} wants to ENTER CS at CLOCK {}.".format(self.process_id, self.clock))
                #print("Process {} wants to ENTER CS at CLOCK {}.".format(self.process_id, self.clock))
                self.__request_to_enter()
                while not self.__allowed_to_enter():
                    self.__receive()

                # Stay in CS for some time ...
                sleep_time = random.randint(0, 2)
                self.logger.debug("Process {} enters CS for {} seconds.".format(self.process_id, sleep_time))
                print("Process {} enters CS for {} seconds.".format(self.process_id, sleep_time))
                print(" Queue{}, Own Clock {}.".format(self.queue, self.clock))

                print(" CS IN  : {}".format(self.process_id.zfill(3)))
                time.sleep(sleep_time)
                print(" CS OUT : {}".format(self.process_id.zfill(3)))
                print()

                # ... then leave CS
                self.__release()
                continue

            # Occasionally serve requests to enter (
            if random.choice([True, False]):
                self.__receive()
