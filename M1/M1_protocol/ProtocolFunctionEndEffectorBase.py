import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionEndEffectorBase(M1_protocol):
    def __init__(self):
        super().__init__()


@M1_protocol.cmd
def setEndEffectorParams(self, x_bias: float, y_bias: float, z_bias: float):
    payload = struct.pack("<fff", x_bias, y_bias, z_bias)
    return M1_msg.build_msg(60, True, self.isQueued, payload), self._decode_indexQueue


@M1_protocol.cmd
def endEffectorParams(self):
    return M1_msg.build_msg(60), self._decode_endEffectorParams


def _decode_endEffectorParams(self, msg):
    _id, write, isqueued, payload = M1_msg.decode_msg(msg)
    x_bias, y_bias_z_bias = struct.unpack("<fff", payload)
