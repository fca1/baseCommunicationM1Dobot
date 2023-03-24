from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol.ProtocolFunctionALARMBase import ProtocolFunctionALARMBase
from M1.M1_protocol.ProtocolFunctionARCBase import ProtocolFunctionARCBase
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import ProtocolFunctionArmOrientationBase
from M1.M1_protocol.ProtocolFunctionCPBase import ProtocolFunctionCPBase
from M1.M1_protocol.ProtocolFunctionDeviceInfoBase import ProtocolFunctionDeviceInfoBase
from M1.M1_protocol.ProtocolFunctionEIOBase import ProtocolFunctionEIOBase
from M1.M1_protocol.ProtocolFunctionEndEffectorBase import ProtocolFunctionEndEffectorBase
from M1.M1_protocol.ProtocolFunctionHHTBase import ProtocolFunctionHHTBase
from M1.M1_protocol.ProtocolFunctionHOMEBase import ProtocolFunctionHOMEBase
from M1.M1_protocol.ProtocolFunctionJOGBase import ProtocolFunctionJOGBase
from M1.M1_protocol.ProtocolFunctionPTPBase import ProtocolFunctionPTPBase
from M1.M1_protocol.ProtocolFunctionPoseBase import ProtocolFunctionPoseBase
from M1.M1_protocol.ProtocolFunctionQueuedCmdBase import ProtocolFunctionQueuedCmdBase
from M1.M1_protocol.ProtocolFunctionTRIGBase import ProtocolFunctionTRIGBase
from M1.M1_protocol.ProtocolFunctionWAITBase import ProtocolFunctionWAITBase
from M1.misc.AngleArm import  AngleArm
from M1.misc.PositionArm import PositionArm




class ProtocolFunction:
    """
    La documentation Dobot explique avoir categrisé les fonctions.
    """
    def __init__(self,comm:M1_comm_udp):
        self.comm = comm
        self.armOrientationBase = ProtocolFunctionArmOrientationBase()
        self.deviceInfoBase = ProtocolFunctionDeviceInfoBase()
        self.poseBase = ProtocolFunctionPoseBase()
        self.alarmBase = ProtocolFunctionALARMBase()
        self.homeBase = ProtocolFunctionHOMEBase()
        self.hhtBase = ProtocolFunctionHHTBase()
        self.cpBase = ProtocolFunctionCPBase()
        self.endEffectorBase = ProtocolFunctionEndEffectorBase()
        self.jogBase  =ProtocolFunctionJOGBase()
        self.ptpBase = ProtocolFunctionPTPBase()
        self.queueCmdBase = ProtocolFunctionQueuedCmdBase()
        self.arcBase = ProtocolFunctionARCBase()
        self.waitBase = ProtocolFunctionWAITBase()
        self.trigBase = ProtocolFunctionTRIGBase()
        self.eioBase = ProtocolFunctionEIOBase()

        pass


    def serial(self) ->str:
        return self.comm.cmd(self.deviceInfoBase.deviceSN, self.deviceInfoBase.decode_deviceSN)


    def pos(self) -> (PositionArm,AngleArm):
        x,y,z,r,*angle =  self.comm.cmd(self.poseBase.pose, self.poseBase.decode_pose)
        return PositionArm(x,y,z,r), AngleArm(*angle)


    @property
    def status_ok(self) ->bool:
        msg =  self.comm.cmd(self.alarmBase.getStatus, self.alarmBase.decode_getStatus)
        return not "error" in msg

    def setClearAllAlarmsState(self):
        self.comm.cmd(self.alarmBase.clearAllAlarmsState, None)