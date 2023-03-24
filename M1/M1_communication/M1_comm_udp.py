import socket


class M1_comm_udp:
    def __init__(self,addr:str,port:int=12345):
        self.bufferSize = 1024
        self.m1AddressPort = (addr, port)
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_msg(self,bytesToSend:bytearray) -> bytes:
        self.client.sendto(bytesToSend, self.m1AddressPort)
        msgFromServer = self.client.recvfrom(self.bufferSize)
        return msgFromServer[0]

    def cmd(self,fcnt:callable,decode:callable,*params):
        x = fcnt(*params)
        answer = self.send_msg(x)
        if decode:
            return decode(answer)
        return answer
