import math
import struct
from dataclasses import dataclass

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.PositionArm import PositionArm


class ProtocolFunctionMiscBase(M1_protocol):
    def __int__(self):
        super().__init__()


def setToolFrame(self, length_arm,axe_arm,height):
    datas = struct.pack('<ffff', axe_arm, length_arm, height, 0)
    msg = M1_msg.build_msg(251, True,self.isQueued,*datas)
    return msg

def setUserFrame(self, pos0:PositionArm,pos1:PositionArm):
    # r est en fait l'angle forme entre X+ et le vecteur P0P1
    slope = (pos1.y - pos0.y)/(pos1.x-pos0.x) if pos1.x-pos0.x else math.inf
    r = math.degrees(math.atan(slope))
    datas = struct.pack('<ffff', pos0.x, pos0.y, pos0.z, r)
    msg = M1_msg.build_msg(250, True,self.isQueued,*datas)
    return msg






