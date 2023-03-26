import struct
from enum import Enum, unique

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol, Velocity, Acceleration


@unique
class E_KEY(Enum):
    IDLE=0       #Invalid status
    XP_DOWN=1    # X+/Joint1+
    XN_DOWN=2    # X-/Joint1-
    YP_DOWN=3    # Y+/Joint2+
    YN_DOWN=4   # Y-/Joint2-
    ZP_DOWN=5    # Z+/Joint3+
    ZN_DOWN=6    # Z-/Joint3-
    RP_DOWN=7    # R+/Joint4+
    RN_DOWN=8    # R-/Joint4-

COORDINATE_MODEL=0  
JOINT_MODEL=1


class ProtocolFunctionJOGBase(M1_protocol):

    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setJOGJointParams(self, velocity: Velocity, acceleration: Acceleration):
        payload = struct.pack("<ffffffff", velocity.x, velocity.y, velocity.z, velocity.r, acceleration.x,
                              acceleration.y, acceleration.z, acceleration.r)
        return M1_msg.build_msg(70, True, self.isQueued, payload), self.decode_indexQueue

    def decode_jogJointParams(self, msg) -> (Velocity, Acceleration):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        x, y, z, r, *acc = struct.unpack("<ffffffff", payload)
        return Velocity(x, y, z, r), Acceleration(*acc)

    @M1_protocol.cmd
    def jogJointParams(self):
        return M1_msg.build_msg(70, True),self.decode_jogJointParams


    @M1_protocol.cmd
    def setCoordinateJointParams(self, velocity: Velocity, acceleration: Acceleration):
        payload = struct.pack("<ffffffff", velocity.x, velocity.y, velocity.z, velocity.r, acceleration.x,
                              acceleration.y, acceleration.z, acceleration.r)
        return M1_msg.build_msg(71, True, self.isQueued, payload), self.decode_indexQueue

    def decode_jogCoordinateParams(self, msg) -> (Velocity, Acceleration):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        x, y, z, r, *acc = struct.unpack("<ffffffff", payload)
        return Velocity(x, y, z, r), Acceleration(*acc)

    @M1_protocol.cmd
    def jogCoordinateParams(self):
        return M1_msg.build_msg(71, True),self.decode_jogCoordinateParams




    @M1_protocol.cmd
    def setJOGCommonParams(self, velocity: float, acceleration: float):
        payload = struct.pack("<ff", velocity, acceleration)
        msg = M1_msg.build_msg(72, True, self.isQueued, payload)
        return msg, self.decode_indexQueue

    @M1_protocol.cmd
    def jogCommonParams(self):
        return  M1_msg.build_msg(72, True,self.isQueued), self.decode_indexQueue





    @M1_protocol.cmd
    def setJOGCmd(self,cmd:E_KEY,isJoint:bool):
        payload = struct.pack("<BB",int(isJoint) ,cmd)
        return  M1_msg.build_msg(72, True, self.isQueued, payload), self.decode_indexQueue