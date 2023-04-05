import logging
import socket
from threading import Lock
from typing import Callable, Any


class M1_comm_udp:
    """
    Le M1 simule la liaison serie a travers une liaison UDP (port) en datagramm
    """

    def __init__(self, addr: str, port: int = 12345):
        self.bufferSize = 1024
        self.m1AddressPort = (addr, port)
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.lock = Lock()

    def send_msg(self, bytesToSend: bytearray) -> bytes:
        with self.lock:
            self.client.sendto(bytesToSend, self.m1AddressPort)
            try:
                msgFromServer = self.client.recvfrom(self.bufferSize)
                return msgFromServer[0]
            except socket.timeout as e:
                raise TimeoutError(f"Timeout msg: {bytesToSend.hex()}")
            pass

    def hookQueuedMsg(msg:bytes, decode_fcnt:Callable) -> Any:
        logging.debug(f"Message: {msg} for queued")
        return None


    def cmd(self, msg_or_tuple: bytes) -> ...:
        """
        Le protocole travaille  selon le principe du ping pong
        :param msg_or_tuple:
        :return: la donnée brute du robot si decode est None sinon variable selon decode.
        """
        msg,askQueued, decode_fcnt = (*msg_or_tuple,) if not isinstance(msg_or_tuple, bytes) else (msg_or_tuple,False, None)
        flg_hook = None
        if askQueued:
            # Il est interessant de pouvoir faire autre chose des messages en destination de queued
            flg_hook = self.hookQueuedMsg(msg,decode_fcnt)
            if flg_hook:
                return flg_hook
        answer = self.send_msg(msg)
        assert askQueued and decode_fcnt            # Toujours une fonction de decodage si queue.
        if decode_fcnt:
            return decode_fcnt(answer)
        return answer

