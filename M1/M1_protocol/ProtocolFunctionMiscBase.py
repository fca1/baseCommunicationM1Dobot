import math
import struct
from dataclasses import dataclass

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.PositionArm import PositionArm


@dataclass
class Param_dynamic:
    # LEs parametres par defaut, sont issus du test fait avec DOBOT M1
    # ce n'est pas publie pour trouver les valeurs.
    zz1:float=0.2617
    fs1:float=0.0565
    fv1:float=0.0459
    zz2:float=7.4010
    mx2:float=0.2404
    my2:float=3.0811
    ia2:float=1.6345
    fs2:float=-0.0198
    fv2:float=1.9735


class ProtocolFunctionMiscBase(M1_protocol):
    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setToolFrame(self, length_arm, axe_arm, height):
        datas = struct.pack('<ffff', axe_arm, length_arm, height, 0)
        msg = M1_msg.build_msg(251, True, self.isQueued, datas)
        return msg, self._decode_indexQueue

    @M1_protocol.cmd
    def setUserFrame(self, pos0: PositionArm, pos1: PositionArm):
        # r est en fait l'angle forme entre X+ et le vecteur P0P1
        slope = (pos1.y - pos0.y) / (pos1.x - pos0.x) if pos1.x - pos0.x else math.inf
        r = math.degrees(math.atan(slope))
        r += 180 if (pos1.x - pos0.x) <= 0 else 0
        datas = struct.pack('<ffff', pos0.x, pos0.y, pos0.z, r)
        msg = M1_msg.build_msg(250, True, self.isQueued, datas)
        return msg, self._decode_indexQueue


    @M1_protocol.cmd
    def dynamicMotionParameter(self):
        return M1_msg.build_msg(202), self._decode_dynamicMotionParameter



    @M1_protocol.cmd
    def setDynamicMotionParameter(self,pd:Param_dynamic ):
        payload = struct.pack("<fffffffff",pd.zz1,pd.fs1,pd.fv1,pd.zz2,pd.mx2,pd.my2,pd.ia2,pd.fs2,pd.fv2 )
        return M1_msg.build_msg(202, True, False, payload)

    def _decode_dynamicMotionParameter(self, msg) -> Param_dynamic:
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        pd = Param_dynamic()
        pd.zz1,pd.fs1,pd.fv1,pd.zz2,pd.mx2,pd.my2,pd.ia2,pd.fs2,pd.fv2 = struct.unpack("<fffffffff", payload)
        return pd


    @M1_protocol.cmd
    def setDynamicPayload(self,charge_kg:float ):
        payload = struct.pack("<f", charge_kg )
        return M1_msg.build_msg(203, True, False, payload)


    @M1_protocol.cmd
    def setSecurityLevelConfiguration(self,tolerateJ1:float,tolerateJ2:float,tolerateJ3:float,tolerateJ4:float):
        # Attention, la velocity se fait avec (80 @ptpJointParams )
        payload = struct.pack("<ffff",tolerateJ1,tolerateJ2,tolerateJ3,tolerateJ4)
        return M1_msg.build_msg(201, True, False, payload)

    @M1_protocol.cmd
    def securityLevelConfiguration(self):
        return M1_msg.build_msg(201, True, False),self._decode_securityLevelConfiguration

    def _decode_securityLevelConfiguration(self,msg):
        tolerateJ1, tolerateJ2, tolerateJ3, tolerateJ4 = struct.unpack("<ffff",msg)
        return tolerateJ1, tolerateJ2, tolerateJ3, tolerateJ4

    @M1_protocol.cmd
    def setRecoveryMode(self,recoveryAfter5sec:bool):
        payload = struct.pack("<BB", 1, recoveryAfter5sec)
        return M1_msg.build_msg(208, True, False,payload)
