import logging
import socket
import constCS
import json


class Server:
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Server")

    telefonbuch = {
        "henning": "12345",
        "tobias": "31313131",
        "Julian": "1001"
    }

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((constCS.HOST, constCS.PORT))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        self.sock.listen(1)
        (connection, address) = self.sock.accept()  # returns new socket and address of client
        while True:  # forever
            data = connection.recv(1024).decode("ascii")  # receive data from client
            if not data:
                break  # stop if client stopped
            elif data.startswith("GETALL"):
                connection.send(json.dumps(self.telefonbuch).encode('ascii'))
            elif data.startswith("GET"):
                if data[3:] in self.telefonbuch.keys():
                    connection.send(self.telefonbuch.get(data[3:]).encode('ascii'))
                else:
                    connection.send("name not found".encode('ascii'))
        connection.close()

    def close(self):
        self.sock.close()
        self.logger.info("Server down")