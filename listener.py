import sys
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM

class receiver:
    PORT_NUMBER = 5000
    SIZE = 1024
    SPEAK = 1.5
    listen = True
    messages = []
    hostName = gethostbyname('0.0.0.0')
    server_addr = None
    received = False
    last_message = "Received"

    mySocket = socket( AF_INET, SOCK_DGRAM )
    mySocket.bind( (hostName, PORT_NUMBER) )

    print ('awake')

    def receive(self):
        while (self.listen):
            (data, address) = self.mySocket.recvfrom(self.SIZE)
            text = str(data)[2:-1]
            if (len(self.messages) > 0 and text == self.messages[-1]):
                self.resend()
            else:
                self.server_addr = address
                self.messages.append(text)
                self.received = True

        quit()

    def send(self, message):
        print (message)
        self.mySocket.sendto(str.encode(message), self.server_addr)
        if (message != 'Received'):
            self.last_message = message

    def resend(self):
        print(self.last_message)
        self.mySocket.sendto(str.encode(self.last_message), self.server_addr)

