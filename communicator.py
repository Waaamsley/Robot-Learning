import sys
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
from time import sleep

class client:

    SERVER_IP   = '192.168.2.2'
    PORT_NUMBER = 5000
    SIZE = 1024
    print("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))
    mySocket = socket(AF_INET, SOCK_STREAM)
    action_complete = True
    mySocket.connect((SERVER_IP, PORT_NUMBER))


    def receive(self):
        (data, address) = self.mySocket.recvfrom(self.SIZE)
        reply = str(data)[2:-1]
        print(reply)
        return reply


    def send(self, message):
        self.mySocket.sendall(str.encode(message))


    def quit(self):
        reply = self.communicate('q', 0.1)
        print('Quit: ', reply)


    def command(self, action):#, rec_client):
        self.action_complete = False
        #action_split = action.split()

        print('Atempting part 1')
        self.send(action)
        reply = self.receive()
        #reply = self.communicate(action, 0.1, False)
        print('Part 1 complete: ', reply)

        print('Atempting part 2')
        reply = self.receive()
        #reply = self.communicate("", 10, True)
        print('Part 2 complete: ', reply)
        
        print(reply, " end of command\n------")

        self.action_complete = True