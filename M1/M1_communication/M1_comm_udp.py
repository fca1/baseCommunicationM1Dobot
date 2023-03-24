import socket


class M1_comm_udp:
    """
    Le M1 simule la liaison serie a travers une liaison UDP (port) en datagramm
    """
    def __init__(self,addr:str,port:int=12345):
        self.bufferSize = 1024
        self.m1AddressPort = (addr, port)
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_msg(self,bytesToSend:bytearray) -> bytes:
        self.client.sendto(bytesToSend, self.m1AddressPort)
        msgFromServer = self.client.recvfrom(self.bufferSize)
        return msgFromServer[0]

    def cmd(self,fcnt:callable,decode:callable,*params) -> ...:
        """
        Le protocole travaille  selon le principe du ping pong
        :param fcnt: Fonction retournant un message bytes
        :param decode: Fonction prenant msg en parametres et permettant de decoder ce dernier
        :param params: parametres additionnels utilisés lors de l'appel de la méthode.
        :return: la donnée brute du robot si decode est None sinon variable selon decode.
        """
        x = fcnt(*params)
        answer = self.send_msg(x)
        if decode:
            return decode(answer)
        return answer
