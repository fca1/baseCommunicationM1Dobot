import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.PositionArm import PositionArm


class ProtocolFunctionCPBase(M1_protocol):

    def __init__(self):
        super().__init__()




@M1_protocol.cmd
def setCPParams(self, planAcc:float,junctionVel:float,acc_period:float,is_realtime:bool):
    payload = struct.pack("<fffB", planAcc,junctionVel,acc_period,is_realtime)
    return M1_msg.build_msg(90, True, self.isQueued, payload), self._decode_indexQueue

@M1_protocol.cmd
def cpParams(self):
    return M1_msg.build_msg(90),self._decode_cpParams

def _decode_cpParams(self,msg):
    _id, write, isqueued, payload = M1_msg.decode_msg(msg)
    planAcc, junctionVel, acc_period, is_realtime =struct.unpack("<fffB",payload)
    return planAcc, junctionVel, acc_period, is_realtime

@M1_protocol.cmd
def setCpCmd(self,point:PositionArm,velocity:float):
    payload = struct.pack("<ffff", point.x,point.y,point.z,velocity)
    return M1_msg.build_msg(91, True, self.isQueued, payload), self._decode_indexQueue



