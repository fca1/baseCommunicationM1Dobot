import struct
from functools import wraps
from typing import Tuple, Any

from M1.M1_protocol.M1_msg import M1_msg


class M1_protocol:
    # utilise par le decorateur, pour pouvoir envoyer ou recevoir un message.
    _fcnt_send_rcve = None

    def __init__(self):
        self._isQueued = False

    def decode_indexQueue(self, msg) -> tuple[Any, ...]:
        id, write, isqueued, payload = M1_msg.decode_msg(msg)
        if isqueued:
            count = struct.unpack("<Q", payload)
            return count
        return None

    @property
    def queued(self):
        # l'appel déclenche le set de la variable
        self._isQueued = True
        return self

    @property
    def isQueued(self):
        # la relire remet a 0
        try:
            return self._isQueued
        finally:
            self._isQueued = False

    @staticmethod
    def cmd(func):
        @wraps(func)
        def send_rcve(*kargs, **kwargs):
            return M1_protocol._fcnt_send_rcve(func(*kargs, **kwargs))

        return send_rcve
        pass
