import struct
from dataclasses import dataclass

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


@dataclass
class Velocity:
    x:float
    y:float
    z:float
    r:float
    def __repr__(self):
        return f"Velocity x={round(self.x)}%,y={round(self.y)}%,z={round(self.z)}%,r={round(self.r)}%"

class Acceleration:
    x:float
    y:float
    z:float
    r:float
    def __repr__(self):
        return f"ACC x={round(self.x)}%,y={round(self.y)}%,z={round(self.z)}%,r={round(self.r)}%"


class ProtocolFunctionPTPBase(M1_protocol):


    def __init__(self):
        super().__init__()


    def ptpJointParams(self):
        msg = M1_msg.build_msg(80)

    def ptpCoordinateParams(self):
        msg = M1_msg.build_msg(81)

    def ptpJointParams(self):
        msg = M1_msg.build_msg(80)

    def setPtpJointParams(self,velocity:Velocity,acceleration:Acceleration):
        payload =struct.pack("<ffffffff", velocity.x,velocity.y,velocity.z,velocity.r,acceleration.x,acceleration.y,acceleration.z,acceleration.r)
        msg = M1_msg.build_msg(80,True,self.isQueued,payload)

    def decode_ptpJointParams(self,msg) -> (Velocity,Acceleration):
        id, write, isqueued, payload = M1_msg.decode_msg(msg)
        x,y,z,r,*acc = struct.unpack("<ffffffff",payload)
        return Velocity(x,y,z,r),Acceleration(*acc)



    def setPtpCoordinateParams(self,velocity_xyz:float,velocity_r:float,acc_xyz:float,acc_r:float):
        payload =struct.pack("<ffff", velocity_xyz,velocity_r,acc_xyz,acc_r)
        msg = M1_msg.build_msg(80,True,self.isQueued,payload)


    def decode_ptpCoordinateParams(self,msg) -> (int,int,int,int):
        id, write, isqueued, payload = M1_msg.decode_msg(msg)
        xyz,r,acc_xyz,acc_r = struct.unpack("<ffff",payload)
        return xyz,r,acc_xyz,acc_r


    def setPtpCommonParams(self, velocity:float, acceleration:float):
        payload =struct.pack("<ff", velocity,  acceleration )
        return M1_msg.build_msg(83,True,self.isQueued,payload)




