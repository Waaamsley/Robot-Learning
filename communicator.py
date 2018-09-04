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
            print(reply)
            return reply
        except error as e:
            print (e)
            if e.errno == errno.ECONNRESET:
                return "-1"
            else:
                sleep(0.5)
            self.mySocket.connect((self.SERVER_IP, self.PORT_NUMBER))
        return "1"


    def send(self, message):
        self.mySocket.sendall(str.encode(message))


    def quit(self):
        reply = self.communicate('q', 0.1)
        print('Quit: ', reply)


    def command(self, action):#, rec_client):
        self.action_complete = False
        #action_split = action.split()

        # print('Atempting part 1')
        reply = "-1"
        while (reply == "-1" or reply == "1"):
            print
            if reply == "-1":
                self.send(action)
            reply = self.receive()
        # print('Part 1 complete: ', reply)

        # print('Atempting part 2')
        reply = "1"
        while reply == "1":
            reply = self.receive()
        # print('Part 2 complete: ', reply)
        
        #print(reply, " end of command\n------")

        self.action_complete = True