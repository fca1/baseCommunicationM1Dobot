import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionPoseBase(M1_protocol):


    def __init__(self):
        super().__init__()


    def pose(self):
        msg = M1_msg.build_msg(10)
        return msg


    def decode_pose(self,msg:bytearray):
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        x,y,z,r,angle_base,angle_rear,angle_form,angle_deflector = struct.unpack("<ffffffff",payload)
        return x,y,z,r,angle_base,angle_rear,angle_form,angle_deflector

    def calibrate(self,frontangle1,frontangle2):
        payload=struct.pack("<Bff",1,frontangle1,frontangle2)
        return M1_msg.build_msg(11,True,False,payload)
