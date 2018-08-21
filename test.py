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
    listen = True
    received = False
    messages = ["Received"]
    last_message = "Received"
    time_check = 0.1

    def receiver(self):
        while (self.listen):
            message_len = len(self.messages)
            self.mySocket.settimeout(self.time_check)

            try:
                (data, address) = self.mySocket.recvfrom(self.SIZE)
                text = str(data)[2:-1]
                if (text == 'Received'):
                    print(text)
                    self.time_check = 5
                elif (text != self.messages[-1]):
                    print(text, self.messages[-1])
                    self.time_check = 0.1
                    self.messages.append(text)
                    self.received = True

            except Exception as e:
                #print(e)
                self.resend()


    def resend(self):
        print("resender: ", self.last_message)
        self.mySocket.sendto(str.encode(self.last_message), (self.SERVER_IP, self.PORT_NUMBER))


    def quit(self):
        self.mySocket.sendto(str.encode('q'), (self.SERVER_IP, self.PORT_NUMBER))

        while (self.received == False):
            continue

        message = self.messages[-1]
        self.received = False

        print(message)


    def command(self, action, rec_client):
        self.action_complete = False
        action_split = action.split()

        rec_client.last_message = action_split[0]
        self.mySocket.sendto(str.encode(action_split[0]), (self.SERVER_IP, self.PORT_NUMBER))
        print('part 1 sent')

        while rec_client.received is False:
            if (len(rec_client.messages) > 0):
                print(rec_client.messages[-1])
            sleep(0.05)

        message = rec_client.messages[-1]
        rec_client.received = False
        print('received ', message)

        print('part 2 sent')
        rec_client.last_message = action_split[1]
        self.mySocket.sendto(str.encode(action_split[1]), (self.SERVER_IP, self.PORT_NUMBER))

        count = 0
        while rec_client.received is False:
            count += 1
            if (count == 5):
                print(rec_client.messages[-1])
                count = 0
            sleep(0.05)

        message = rec_client.messages[-1]
        rec_client.received = False
        print(message, " end of command")

        self.action_complete = True