import struct
from enum import Enum, unique

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.ProtocolFunction import ProtocolFunction


@unique
class E_ptpMode(Enum): 
    JUMP_XYZ=0 # JUMP mode, (x,y,z,r) is the target point in Cartesian coordinate system
    MOVJ_XYZ=1 # MOVJ mode, (x,y,z,r) is the target point in Cartesian coordinate system
    MOVL_XYZ=2 #MOVL mode, (x,y,z,r) is the target point in Cartesian coordinate system
    JUMP_ANGLE=3 # JUMP mode, (x,y,z,r) is the target point in Joint coordinate system
    MOVJ_ANGLE=4 # MOVJ mode, (x,y,z,r) is the target point in Joint coordinate system
    MOVL_ANGLE=5 # MOVL mode, (x,y,z,r) is the target point in Joint coordinate system
    MOVJ_INC=6 # MOVJ mode, (x,y,z,r) is the angle increment in Joint coordinate system
    MOVL_INC=7 # MOVL mode, (x,y,z,r) is the Cartesian coordinate increment in Joint coordinate system
    MOVJ_XYZ_INC=8 # MOVJ mode, (x,y,z,r) is the Cartesian coordinate increment in Cartesian coordinate system
    JUMP_MOVL_XYZ=9 # JUMP mode, (x,y,z,r) is the Cartesian coordinate increment in Cartesian coordinate system


class ProtocolFunctionArmOrientationBase(ProtocolFunction):
    def __int__(self):
        super().__init__()

    @staticmethod
    def setPTPCmd(x:float,y:float,z:float,r:float,mode:E_ptpMode=E_ptpMode.MOVJ_XYZ,isQueued:bool=False) -> bytearray:

        "aa aa 13 54 03 01 (00 00 2c c3) (00 00 48 42) (00 00 00 10)   25 c3 00 00 c8 42 3d"

        datas = struct.pack('>Bffff',mode.value, x, y, z, r)
        msg = M1_msg.build_msg(0x54,True,isQueued, *datas)
        return msg


