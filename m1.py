import logging
import time

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.AngleArm import AngleArm
from M1.misc.PositionArm import PositionArm


class M1:
    MAX_HEIGHT = 234
    PT_EXTENDED = (400, 0, MAX_HEIGHT, 0)

    def __init__(self, ip_addr="192.168.1.60"):
        self.protocol = CommProtocolM1(ip_addr)
        self.protocol.setTimeout(5)
        self.initialAngleDefector = 0
        self.is_ok()
        self.protocol.hhtBase.queued.setHttTrigOutputEnabled(False)
        reason = self.protocol.alarm
        if reason == 68:
            # Z trop haut, un seul moyen couper le moteur
            self.protocol.hhtBase.queued.setHttTrigOutputEnabled(True)
            time.sleep(2)
            self.protocol.hhtBase.queued.setHttTrigOutputEnabled(False)
            reason = self.protocol.alarm
        if reason == 69:
            self.protocol.armOrientationBase.setPTPCmd(
                AngleArm(0, 0, 30, 0), E_ptpMode.MOVJ_INC
            )

        while reason := self.protocol.alarm:
            logging.warning(f"Erreur sur le M1: error ={reason}")
            self.protocol.alarmBase.clearAllAlarmsState()
        # Nettoyer la queue de messages
        self.protocol.queueCmdBase.setQueuedCmdForceStopExec()
        self.protocol.queueCmdBase.setQueuedCmdClear()
        self.protocol.queueCmdBase.setQueuedCmdStartExec()
        pass

    def wait_idle(self):
        # protocol.homeBase.setHome()
        while self.protocol.status == "ran":
            time.sleep(2)

    def is_ok(self):
        try:
            # Initialiser le systeme de communication udp
            # Detection presence du M1
            reason = self.protocol.alarm
            if reason:
                print(f"Erreur sur le M1: error ={reason}")
                self.protocol.alarmBase.clearAllAlarmsState()
                self.protocol.homeBase.setHome()
            serial = self.protocol.serial()
            return bool(serial)
        except Exception as e:
            logging.warning(f"Pb {e}")
            return False

    def initialize_origin(self):
        # Mettre l'origine a 200
        homing_position = PositionArm(*self.PT_EXTENDED)
        p0 = PositionArm(-400, 0, -self.MAX_HEIGHT) + homing_position
        p1 = PositionArm(0, 0, -self.MAX_HEIGHT) + homing_position
        self.protocol.miscBase.setUserFrame(p1, p0)  # user tool

    def setHome(self):
        # Mettre alimentation sur le robot
        self.protocol.ptpBase.queued.setPtpCommonParams(20, 20)
        self.protocol.hhtBase.queued.setHttTrigOutputEnabled(False)
        # monter la tete sans rien faire d'autre
        offset0 = self.protocol.angle
        offset0.front = self.MAX_HEIGHT
        self.protocol.armOrientationBase.queued.setPTPCmd(offset0, E_ptpMode.MOVJ_ANGLE)
        offset0 = AngleArm(0, 0, self.MAX_HEIGHT, self.initialAngleDefector)
        self.wait_end_queue(
            self.protocol.armOrientationBase.queued.setPTPCmd(
                offset0, E_ptpMode.MOVJ_ANGLE
            )
        )

    def initialize_length_defector(self, length):
        self.protocol.miscBase.setToolFrame(length, 0, 0)

    def initialize_arm(self, right=True):
        # Choisir une orientation et passer sur un point intermediaire apres avoir géré acceleration
        self.protocol.armOrientationBase.queued.setArmOrientation(right)

    def wait_end_queue(self, index_wait: int):
        while index_wait > self.protocol.queueCmdBase.queuedCmdCurrentIndex():
            time.sleep(0.2)

    @property
    def pos(self) -> PositionArm:
        return self.protocol.pos


if __name__ == "__main__":
    m1 = M1()
    m1.initialize_origin()
    m1.setHome()
    m1.initialize_arm()
    # Mettre la hauteur frontiere a 200 et 220
    m1.protocol.ptpBase.queued.setPtpJumpParams(20, 150)
    pos = m1.pos
    pos.z = 100
    m1.protocol.ptpBase.queued.setPtpCommonParams(1, 6)
    m1.protocol.armOrientationBase.queued.setPTPCmd(pos, E_ptpMode.MOVJ_XYZ)
    pos.x = 100
    pos.y = -100
    m1.protocol.armOrientationBase.queued.setPTPCmd(pos, E_ptpMode.JUMP_XYZ)
    pass
