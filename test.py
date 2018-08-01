import sys
from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep
class client:

    SERVER_IP   = '192.168.2.2'
    PORT_NUMBER = 5000
    SIZE = 1024
    print("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))
    mySocket = socket(AF_INET, SOCK_DGRAM)
    action_complete = True

    def quit(self):
        self.mySocket.sendto(str.encode('q'), (self.SERVER_IP, self.PORT_NUMBER))

        (data, address) = self.mySocket.recvfrom(self.SIZE)
        message = str(data)[2:-1]
        print(message)


    def command(self, action):
        self.action_complete = False
        action_split = action.split()
        self.mySocket.sendto(str.encode(action_split[0]), (self.SERVER_IP, self.PORT_NUMBER))

        (data, address) = self.mySocket.recvfrom(self.SIZE)
        message = str(data)[2:-1]
        print(message)
        sleep(0.5)

        self.mySocket.sendto(str.encode(action_split[1]), (self.SERVER_IP, self.PORT_NUMBER))

        (data, address) = self.mySocket.recvfrom(self.SIZE)
        message = str(data)[2:-1]
        print(message)
        sleep(1)
        self.action_complete = True