import socket


class M1_comm_udp:
    """
    Le M1 simule la liaison serie a travers une liaison UDP (port) en datagramm
    """

    def __init__(self, addr: str, port: int = 12345):
        self.bufferSize = 1024
        self.m1AddressPort = (addr, port)
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def send_msg(self, bytesToSend: bytearray) -> bytes:
        self.client.sendto(bytesToSend, self.m1AddressPort)
        try:
            msgFromServer = self.client.recvfrom(self.bufferSize)
        except socket.timeout as e:

            raise TimeoutError(f"Timeout msg: {bytesToSend.hex()}")
            pass

        return msgFromServer[0]

    def cmd(self, msg_or_tuple: bytes) -> ...:
        """
        Le protocole travaille  selon le principe du ping pong
        :param msg_or_tuple:
        :return: la donnée brute du robot si decode est None sinon variable selon decode.
        """
        x, decode_fcnt = (*msg_or_tuple,) if not isinstance(msg_or_tuple, bytes) else (msg_or_tuple, None)
        answer = self.send_msg(x)
        if decode_fcnt:
            return decode_fcnt(answer)
        return answer
