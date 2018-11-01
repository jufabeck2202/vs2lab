import constRPC
import threading
import time

from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self


class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')
        self.received_list = []

    def run(self):
        """
        wait for append data
        :return:
        """
        print("\t Thread: Waiting for response")
        msgrcv = self.chan.receive_from(self.server)  # wait for response
        print("\t Thread: Received response, closing thread")
        self.received_list = msgrcv[1]

    def stop(self):
        self.chan.leave('client')

    def wait_for_Ack(self):
        msgrcv = self.chan.receive_from(self.server)
        if msgrcv[1] == "ok":
            #continue, start wait for append
            print("Client: received ACK from server, continue progamm")
            return

    def append(self, data, db_list):
        assert isinstance(db_list, DBList)
        msglst = (constRPC.APPEND, data, db_list)  # message payload
        self.chan.send_to(self.server, msglst)  # send msg to server
        self.wait_for_Ack()
        self.start()
        print("Client: Doing other stuff")
        print("Client: Working hard while waiting for a response")
        print("Client: Working so so so hard")
        self.join()
        print("Client: thread closed, received response")
        return self.received_list


class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)  # - Make sure we have a list
        return db_list.append(data)

    @staticmethod
    def sendAck(client,chan):
        """
        Notify client
        :param client:
        :param chan:
        :return:
        """
        print("Server: Send Ack to client")
        chan.send_to({client}, "ok")

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)  # wait for any request
            if msgreq is not None:
                client = msgreq[0]  # see who is the caller
                msgrpc = msgreq[1]  # fetch call & parameters
                self.sendAck(client, self.chan)
                if constRPC.APPEND == msgrpc[0]:  # check what is being requested
                    print("Server: Processing Request")
                    time.sleep(2)
                    print("Server: Finished processing Request")
                    result = self.append(msgrpc[1], msgrpc[2])  # do local call
                    self.chan.send_to({client}, result)  # return response
                else:
                    pass  # unsupported request, simply ignore
