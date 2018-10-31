import logging
import socket
import constCS
import json

class User:
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((constCS.HOST, constCS.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def get_user(self, name="henning"):
        self.sock.send(("GET"+name).encode('ascii'))  # send encoded string as data
        number = self.sock.recv(1024)  # receive the response
        msg_out = number.decode('ascii')
        print("Number:"+msg_out)  # print the result
        #self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out

    def get_all(self):
        socket_str = "GETALL"
        self.sock.send(socket_str.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        telefonbuch = json.loads(data.decode('ascii'))
        print(telefonbuch)  # print the result
        #self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return telefonbuch
    def client_close(self):
        self.sock.close()