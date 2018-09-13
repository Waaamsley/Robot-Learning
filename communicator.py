import sys
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, error
import errno
from time import sleep

class client:

    def __init__(self):
        self.SERVER_IP   = '192.168.2.2'
        self.PORT_NUMBER = 5000
        self.SIZE = 1024
        #print("Test client sending packets to IP {0}, via port {1}\n".format(self.SERVER_IP, self.PORT_NUMBER))
        self.mySocket = socket(AF_INET, SOCK_STREAM)
        self.action_complete = True
        self.mySocket.connect((self.SERVER_IP, self.PORT_NUMBER))


    def close_connection(self):
        self.mySocket.close()


    def receive(self):
        try:
            (data, address) = self.mySocket.recvfrom(self.SIZE)
            reply = str(data)[2:-1]
            # print(reply)
            return reply
        except error as e:
            print (e)

    def send(self, message):
        self.mySocket.sendall(str.encode(message))


    def quit(self):
        reply = self.communicate('q', 0.1)
        print('Quit: ', reply)


    def command(self, action):
        self.action_complete = False

        self.send(action)
        reply = self.receive()
        # print('Part 1 complete: ', reply)

        reply = self.receive()
        # print('Part 2 complete: ', reply)

        self.action_complete = True