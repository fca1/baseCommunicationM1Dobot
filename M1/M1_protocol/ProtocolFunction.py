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
from M1.M1_protocol.ProtocolFunctionMiscBase import ProtocolFunctionMiscBase
from M1.M1_protocol.ProtocolFunctionPTPBase import ProtocolFunctionPTPBase, Acceleration, Velocity
from M1.M1_protocol.ProtocolFunctionPoseBase import ProtocolFunctionPoseBase
from M1.M1_protocol.ProtocolFunctionQueuedCmdBase import ProtocolFunctionQueuedCmdBase
from M1.M1_protocol.ProtocolFunctionTRIGBase import ProtocolFunctionTRIGBase
from M1.M1_protocol.ProtocolFunctionWAITBase import ProtocolFunctionWAITBase




class ProtocolFunction:
    """
    La documentation Dobot explique avoir categrisé les fonctions.
    """
    def __init__(self):
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
        self.miscBase = ProtocolFunctionMiscBase()

        pass


