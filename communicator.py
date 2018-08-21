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

    def communicate(self, message, timeout, recv_only):
        reply = None
        if not recv_only:
            self.mySocket.sendto(str.encode(message), (self.SERVER_IP, self.PORT_NUMBER))

        persist = True
        while (persist):
            self.mySocket.settimeout(timeout)
            try:
                (data, address) = self.mySocket.recvfrom(self.SIZE)
                reply = str(data)[2:-1]
                persist = False
            except Exception as e:
                print(e, timeout)
                if not recv_only:
                    self.mySocket.sendto(str.encode(message), (self.SERVER_IP, self.PORT_NUMBER))
                else:
                    persist = False
        
        return reply
        

    def quit(self):
        reply = self.communicate('q', 0.1)
        print('Quit: ', reply)


    def command(self, action):#, rec_client):
        self.action_complete = False
        #action_split = action.split()

        print('Atempting part 1')
        reply = self.mySocket.communicate(action, 0.1, False)
        print('Part 1 complete: ', reply)

        print('Atempting part 2')
        reply = self.mySocket.communicate("", 5, True)
        print('Part 2 complete: ', reply)
        
        print(reply, " end of command")

        self.action_complete = True