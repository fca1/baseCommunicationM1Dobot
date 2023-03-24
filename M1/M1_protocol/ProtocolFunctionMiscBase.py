import struct
from dataclasses import dataclass

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.PositionArm import PositionArm


class ProtocolFunctionMiscBase(M1_protocol):
    def __int__(self):
        super().__init__()


def setToolFrame(self,pos:PositionArm):
    datas = struct.pack('<ffff',  pos.x, pos.y, pos.z, pos.r)
    msg = M1_msg.build_msg(251, True,self.isQueued,*datas)
    return msg

def setUserFrame(self, pos0:PositionArm,pos1:PositionArm):
    datas = struct.pack('<ffff', pos0.x, pos0.y, pos0.z, pos0.r)
    msg = M1_msg.build_msg(250, True,self.isQueued,*datas)
    return msg






