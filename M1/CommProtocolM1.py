from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol.ProtocolFunction import ProtocolFunction
from M1.M1_protocol.ProtocolFunctionPTPBase import Acceleration, Velocity
from M1.misc.AngleArm import AngleArm
from M1.misc.PositionArm import PositionArm


class CommProtocolM1(M1_comm_udp,ProtocolFunction):
    def __init__(self,addr:str,port:int=12345):
        super(M1_comm_udp).__init__(addr,port)
        super(ProtocolFunction).__init__()


    def cmd(self,fcnt:callable,*params) -> ...:
        """
        Le protocole travaille  selon le principe du ping pong
        :param fcnt: Fonction retournant un message bytes
        :param decode: Fonction prenant msg en parametres et permettant de decoder ce dernier
        :param params: parametres additionnels utilisés lors de l'appel de la méthode.
        :return: la donnée brute du robot si decode est None sinon variable selon decode.
        """
        msg_or_tuple = fcnt
        x,decode_fcnt = (*msg_or_tuple,) if not isinstance(msg_or_tuple,bytes) else (msg_or_tuple,None)
        answer = self.send_msg(x)
        if decode_fcnt:
            return decode_fcnt(answer)
        return answer

    def serial(self) ->str:
        return self.comm.cmd(self.deviceInfoBase.deviceSN)

    @property
    def pos(self) -> (PositionArm,AngleArm):
        x,y,z,r,*angle =  self.comm.cmd(self.poseBase.pose)
        return PositionArm(x,y,z,r), AngleArm(*angle)


    @property
    def status_ok(self) ->bool:
        return not "error" in self.status

    @property
    def status(self)->str:
        return self.cmd(self.alarmBase.status)

    def setClearAllAlarmsState(self):
        self.cmd(self.alarmBase.clearAllAlarmsState)


    def setPtpCoordinateParams(self,velocity:Velocity,acc:Acceleration):
        self.cmd(self.ptpBase.setPtpJointParams())