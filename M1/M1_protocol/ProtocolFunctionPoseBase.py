import struct

from M1.M1_protocol.M1_msg import M1_msg


class ProtocolFunctionPoseBase():


    def __int__(self):
        super().__init__()


    def pose(self):
        msg = M1_msg.build_msg(10)
        return msg


    def decode_pose(self,msg:bytearray):
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        x,y,z,r,angle_base,angle_rear,angle_form,angle_deflector = struct.unpack(">ffffffff",payload)
        return x,y,z,r
