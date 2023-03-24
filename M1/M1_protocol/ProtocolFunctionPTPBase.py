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
        """
        This command is to get the velocity and acceleration of the joint coordinate axes in PTP
        mode, the issued command packet is shown in Table 68, and the returned command packet
        is shown in Table 69.
        """
        return M1_msg.build_msg(80)

    def ptpCoordinateParams(self):
        """
        This command is to set the velocity and acceleration of the Cartesian coordinate axes in
        PTP mode, the issued command packet is shown in Table 70, and the returned command
        packet is shown in Table 71.
        :return:
        """
        return M1_msg.build_msg(81)


    def setPtpJointParams(self,velocity:Velocity,acceleration:Acceleration):
        payload =struct.pack("<ffffffff", velocity.x,velocity.y,velocity.z,velocity.r,acceleration.x,acceleration.y,acceleration.z,acceleration.r)
        return M1_msg.build_msg(80,True,self.isQueued,*payload)

    def decode_ptpJointParams(self,msg) -> (Velocity,Acceleration):
        id, write, isqueued, payload = M1_msg.decode_msg(msg)
        x,y,z,r,*acc = struct.unpack("<ffffffff",payload)
        return Velocity(x,y,z,r),Acceleration(*acc)



    def setPtpCoordinateParams(self,velocity_xyz:float,velocity_r:float,acc_xyz:float,acc_r:float):
        payload =struct.pack("<ffff", velocity_xyz,velocity_r,acc_xyz,acc_r)
        return M1_msg.build_msg(81,True,self.isQueued,*payload)


    def decode_ptpCoordinateParams(self,msg) -> (int,int,int,int):
        id, write, isqueued, payload = M1_msg.decode_msg(msg)
        xyz,r,acc_xyz,acc_r = struct.unpack("<ffff",payload)
        return xyz,r,acc_xyz,acc_r


    def setPtpCommonParams(self, velocity:float, acceleration:float):
        """
        This command is to set the velocity ratio and the acceleration ratio in PTP mode, the issued
        command packet is shown in Table 78, and the returned command packet is shown in
        Table 79.
        Ta
        :param velocity:
        :param acceleration:
        :return:
        """
        payload =struct.pack("<ff", velocity,  acceleration )
        msg = M1_msg.build_msg(83,True,self.isQueued,payload)

        return M1_msg.build_msg(83,True,self.isQueued,payload)

    def ptpJumpParams(self) :
        """
        float jumpHeight; //Lifting height in Jump mode
        float zLimit; //Maximum lifting height in Jump mod
        """
        return M1_msg.build_msg(82)

    def decode_ptpJumpParams(self,msg) ->(int,int):
        """
        float jumpHeight; //Lifting height in Jump mode
        float zLimit; //Maximum lifting height in Jump mod
        """
        id, write, isqueued, payload = M1_msg.decode_msg(msg)
        jumpHeight,zLimit = struct.unpack("<ff",payload)
        return jumpHeight,zLimit

    def setPtpJumpParams(self,jumpHeight:float,zLimit:float):
        """
        This command is to get the lifting height and the maximum lifting height in JUMP mode,
        the issued command packet is shown in Table 76, and the returned command packet is
        shown in Table 77
        :param jumpHeight:
        :param zLimit:
        :return:
        """
        payload =struct.pack("<ff", jumpHeight,  zLimit )
        msg = M1_msg.build_msg(82,True,self.isQueued,payload)
        return msg


