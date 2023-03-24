from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol.ProtocolFunctionALARMBase import ProtocolFunctionALARMBase
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import ProtocolFunctionArmOrientationBase
from M1.M1_protocol.ProtocolFunctionDeviceInfoBase import ProtocolFunctionDeviceInfoBase
from M1.M1_protocol.ProtocolFunctionHHTBase import ProtocolFunctionHHTBase
from M1.M1_protocol.ProtocolFunctionHOMEBase import ProtocolFunctionHOMEBase
from M1.M1_protocol.ProtocolFunctionPoseBase import ProtocolFunctionPoseBase
from M1.misc.AngleArm import  AngleArm
from M1.misc.PositionArm import PositionArm


class ProtocolFunction:
    def __init__(self,comm:M1_comm_udp):
        self.comm = comm
        self.armOrientationBase = ProtocolFunctionArmOrientationBase()
        self.deviceInfoBase = ProtocolFunctionDeviceInfoBase()
        self.poseBase = ProtocolFunctionPoseBase()
        self.alarmBase = ProtocolFunctionALARMBase()
        self.homeBase = ProtocolFunctionHOMEBase()
        self.hhtBase = ProtocolFunctionHHTBase()

        pass

    @property
    def serial(self):
        return self.comm.cmd(self.deviceInfoBase.deviceSN, self.deviceInfoBase.decode_deviceSN)


    def getPos(self) -> (PositionArm,AngleArm):
        x,y,z,r,*angle =  self.comm.cmd(self.poseBase.pose, self.poseBase.decode_pose)
        return PositionArm(x,y,z,r), AngleArm(*angle)

