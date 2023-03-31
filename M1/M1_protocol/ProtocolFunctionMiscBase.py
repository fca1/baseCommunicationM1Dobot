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


    zz1:float=0.30660000443458557
    fs1:float=0.05920000001788139
    fv1:float=0.07440000027418137
    zz2:float=7.1427998542785645
    mx2:float=0.3237999975681305
    my2:float=3.0055999755859375
    ia2:float=1.7759000062942505
    fs2:float=-0.010999999940395355
    fv2:float=8559000492095947


class ProtocolFunctionMiscBase(M1_protocol):
    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setToolFrame(self, length_arm:float, axe_arm:float, height:float):
        datas = struct.pack('<ffff', length_arm, axe_arm, height,0)
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
    def dynamicPayload(self):

        return M1_msg.build_msg(203),self._decode_dynamicPayload

    def _decode_dynamicPayload(self,msg):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        charge_kg = struct.unpack("<f",payload)
        return charge_kg

    @M1_protocol.cmd
    def setSecurityLevelConfiguration(self,tolerateJ1:float,tolerateJ2:float,tolerateJ3:float,tolerateJ4:float):
        # Attention, la velocity se fait avec (80 @ptpJointParams )
        payload = struct.pack("<ffff",tolerateJ1,tolerateJ2,tolerateJ3,tolerateJ4)
        return M1_msg.build_msg(201, True, False, payload)

    @M1_protocol.cmd
    def securityLevelConfiguration(self):
        return M1_msg.build_msg(201),self._decode_securityLevelConfiguration

    def _decode_securityLevelConfiguration(self,msg):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        tolerateJ1, tolerateJ2, tolerateJ3, tolerateJ4 = struct.unpack("<ffff",payload)
        return tolerateJ1, tolerateJ2, tolerateJ3, tolerateJ4

    @M1_protocol.cmd
    def setRecoveryMode(self, enableImmediatly:bool):
        payload = struct.pack("<B", enableImmediatly)
        return M1_msg.build_msg(208, True, False,payload)

    @M1_protocol.cmd
    def recoveryMode(self):
        return M1_msg.build_msg(208),self._decode_recoveryMode

    def _decode_recoveryMode(self,msg):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        p1 = struct.unpack("<B", payload)
        return p1