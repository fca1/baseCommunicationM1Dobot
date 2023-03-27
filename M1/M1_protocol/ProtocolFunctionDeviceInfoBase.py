from typing import Callable

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionDeviceInfoBase(M1_protocol):

    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def deviceSN(self) -> (bytes, Callable):
        msg = M1_msg.build_msg(0x00)
        return msg, self._decode_deviceSN

    def _decode_deviceSN(self, msg: bytearray):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        return payload[:-1].decode()
        pass
