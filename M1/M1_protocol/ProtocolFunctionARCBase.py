import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.PositionArm import PositionArm


class ProtocolFunctionARCBase(M1_protocol):
    def __init__(self):
        super().__init__()





@M1_protocol.cmd
def setArcParams(self, velocity_xyz: float, velocity_r: float, acc_xyz: float, acc_r: float):
    payload = struct.pack("<ffff", velocity_xyz, velocity_r, acc_xyz, acc_r)
    return M1_msg.build_msg(100, True, self.isQueued, payload), self._decode_indexQueue

@M1_protocol.cmd
def arcParams(self):
    return M1_msg.build_msg(100),self._decode_arcParams

def _decode_arcParams(self,msg):
    _id, write, isqueued, payload = M1_msg.decode_msg(msg)
    xyz, r, acc_xyz, acc_r = struct.unpack("<ffff", payload)
    return xyz, r, acc_xyz, acc_r

@M1_protocol.cmd
def setArcCmd(self,p0:PositionArm,p1:PositionArm):
    payload = struct.pack("<ffff", p0.x, p0.y, p0.z, p0.r,p1.x, p1.y, p1.z, p1.r,)
    return M1_msg.build_msg(101, True, self.isQueued, payload), self._decode_indexQueue

