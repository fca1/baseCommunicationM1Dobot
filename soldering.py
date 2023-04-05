import logging
import time

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.AngleArm import AngleArm
from M1.misc.PositionArm import PositionArm


class Soldering:
    MAX_HEIGHT=234
    PT_EXTENDED=(400,0,MAX_HEIGHT,0)
    def __init__(self,ip_addr="192.168.0.55"):
        self.protocol = CommProtocolM1(ip_addr)
        self.protocol.setTimeout(5)
        self.initialAngleDefector = 0
        self.is_ok()
        reason = self.protocol.alarm
        if reason:
            print(f"Erreur sur le M1: error ={reason}")
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
            serial = self.protocol.serial()
            return bool(serial)
        except Exception as e:
            logging.warning(f"Pb {e}")
            return False


    def place_to_home(self):
        # Mettre alimentation sur le robot
        self.protocol.ptpBase.setPtpCommonParams(50, 50)
        self.protocol.hhtBase.setHttTrigOutputEnabled(False)
        # Mettre l'origine a 200
        homing_position = PositionArm(*self.PT_EXTENDED)
        p0 = PositionArm(200, 0, -self.MAX_HEIGHT) + homing_position
        p1 = PositionArm(-200, 0, -self.MAX_HEIGHT) + homing_position
        self.protocol.miscBase.setUserFrame(p1, p0)  # user tool

        offset0 = AngleArm(1,1,self.MAX_HEIGHT,self.initialAngleDefector)
        self.protocol.armOrientationBase.setPTPCmd(offset0,E_ptpMode.MOVJ_ANGLE)
        self.wait_idle()

    def initialize_length_defector(self):
        self.protocol.miscBase.setToolFrame(70,0,0)
        self.protocol.armOrientationBase.setPTPCmd(PositionArm(250, 0, 0, self.initialAngleDefector), E_ptpMode.MOVJ_XYZ)

    def initialize_arm(self):
        # Choisir une orientation et passer sur un point intermediaire apres avoir géré acceleration
        self.protocol.armOrientationBase.queued.setArmOrientation(True)

    def wait_end_queue(self,index_wait:int):
        while (index_wait > self.protocol.queueCmdBase.queuedCmdCurrentIndex()):
            time.sleep(0.2)
