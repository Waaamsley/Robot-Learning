import sys
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM, SOCK_STREAM

class receiver:
    PORT_NUMBER = 5000
    SIZE = 1024
    SPEAK = 1.5
    hostName = gethostbyname('0.0.0.0')
    server_addr = None

    mySocket = socket(AF_INET, SOCK_STREAM)
    mySocket.bind((hostName, PORT_NUMBER))

    print ('awake')

    mySocket.listen(1)
    connection, server_addr = mySocket.accept()


    def receive(self):
        try:
            (data, address) = self.connection.recvfrom(self.SIZE)
            self.server_addr = address
            reply = str(data)[2:-1]
            return reply
        except Exception as e:
            print (e)

    def send(self, message):
        self.connection.sendall(str.encode(message))
