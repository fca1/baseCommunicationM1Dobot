import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.PositionArm import PositionArm


class ProtocolFunctionHOMEBase(M1_protocol):
    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setHome(self):
        msg = M1_msg.build_msg(31, True)
        return msg

    @M1_protocol.cmd
    def home(self):
        msg = M1_msg.build_msg(30)
        return msg, self._decode_home

    def _decode_home(self, msg):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        x, y, z, r = struct.unpack("<ffff", payload)
        return PositionArm(x, y, z, r)

    @M1_protocol.cmd
    def setHomeSwitch(self, calibrate: bool = False):
        datas = struct.pack("<B", calibrate)
        msg = M1_msg.build_msg(33, True, self.isQueued, datas)
        return msg, self._decode_indexQueue
