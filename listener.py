import sys
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM

class receiver:
    PORT_NUMBER = 5000
    SIZE = 1024
    SPEAK = 1.5
    hostName = gethostbyname('0.0.0.0')
    server_addr = None

    mySocket = socket( AF_INET, SOCK_DGRAM )
    mySocket.bind( (hostName, PORT_NUMBER) )

    print ('awake')

    def communicate(self, message, timeout, recv_only):
        reply = None
        if not recv_only:
            self.mySocket.sendto(str.encode(message), (self.SERVER_IP, self.PORT_NUMBER))

        persist = True
        while (persist):
            self.mySocket.settimeout(timeout)
            try:
                (data, address) = self.mySocket.recvfrom(self.SIZE)
                if recv_only:
                    reply = str(data)[2:-1]
                    persist = False
                else:
                    self.mySocket.sendto(str.encode(message), (self.SERVER_IP, self.PORT_NUMBER))
            except Exception as e:
                print(e, timeout)
                if not recv_only:
                    persist = False
        
        return reply
