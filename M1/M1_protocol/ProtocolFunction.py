from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import ProtocolFunctionArmOrientationBase
from M1.M1_protocol.ProtocolFunctionDeviceInfoBase import ProtocolFunctionDeviceInfoBase
from M1.M1_protocol.ProtocolFunctionPoseBase import ProtocolFunctionPoseBase


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

