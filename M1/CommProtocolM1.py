from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol.M1_protocol import M1_protocol, Acceleration, Velocity
from M1.M1_protocol.ProtocolFunction import ProtocolFunction
from M1.misc.AngleArm import AngleArm
from M1.misc.PositionArm import PositionArm


class CommProtocolM1(M1_comm_udp, ProtocolFunction):
    def __init__(self, addr: str, port: int = 12345):
        M1_comm_udp.__init__(self, addr, port)
        ProtocolFunction.__init__(self)
        # utilise par le decorateur pour pouvoir envoyer et recevoir des messages.

        M1_protocol._fcnt_send_rcve = self.cmd

    def cmd(self, fcnt: callable, *params) -> ...:
        """
        Le protocole travaille  selon le principe du ping pong
        :param fcnt: Fonction retournant un message bytes
        :param params: parametres additionnels utilisés lors de l'appel de la méthode.
        :return: la donnée brute du robot si decode est None sinon variable selon decode.
        """
        msg_or_tuple = fcnt
        x, decode_fcnt = (
            (*msg_or_tuple,)
            if not isinstance(msg_or_tuple, bytes)
            else (msg_or_tuple, None)
        )
        answer = self.send_msg(x)
        if decode_fcnt:
            return decode_fcnt(answer)
        return answer

    @property
    def alarm(self):
        return self.alarmBase.alarm()

    def serial(self) -> str:
        return self.deviceInfoBase.deviceSN()

    @property
    def pos(self) -> PositionArm:
        x, y, z, r, *angle = self.poseBase.pose()
        return PositionArm(x, y, z, r)

    @property
    def angle(self) -> AngleArm:
        x, y, z, r, *angle = self.poseBase.pose()
        return AngleArm(*angle)

    @property
    def status_ok(self) -> bool:
        return not "error" in self.status

    @property
    def status(self) -> str:
        return self.alarmBase.status()

    def setClearAllAlarmsState(self):
        self.alarmBase.clearAllAlarmsState()

    def setTimeout(self, timeout):
        self.client.settimeout(timeout)
