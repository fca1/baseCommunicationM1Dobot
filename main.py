import time

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.M1_protocol.ProtocolFunctionJOGBase import E_KEY
from M1.M1_protocol.ProtocolFunctionMiscBase import Param_dynamic
from M1.misc.PositionArm import PositionArm
from M1.misc.AngleArm import AngleArm

# Initialiser le systeme de communication udp

protocol = CommProtocolM1("192.168.0.55")
protocol.setTimeout(5)

# Detection presence du M1
assert protocol.serial()

# Mettre alimentation sur le robot
protocol.hhtBase.setHttTrigOutputEnabled(False)
# Pas d'impulsion sur la sortie
protocol.eioBase.setDo(1,False)



# Lire les alarms
reason = protocol.alarm
if reason:
    print(f"Erreur sur le M1: error ={reason}")
    protocol.alarmBase.clearAllAlarmsState()

# Nettoyer la queue de messages
protocol.queueCmdBase.setQueuedCmdForceStopExec()
protocol.queueCmdBase.setQueuedCmdClear()
# Faire un homing (Attention R ? )

initialAngleDefector = 0

if 1:
    #protocol.homeBase.setHome()
    while protocol.status == "ran":
        time.sleep(2)
    # Mettre l'origine a 200
    homing_position = PositionArm(400, 0, 0)
    p0 = PositionArm(200, 0, 230) + homing_position
    p1 = PositionArm(-200, 0, 230) + homing_position
    protocol.miscBase.setUserFrame(p1, p0)  # user tool

    offset0 = AngleArm(0,0,230,initialAngleDefector)
    protocol.armOrientationBase.setPTPCmd(offset0,E_ptpMode.MOVJ_ANGLE)
    while protocol.status == "ran":
        time.sleep(2)

    # declarer le defector a 70,50 (y)
    for i in range(0,100,10):
        protocol.miscBase.setToolFrame(70,i,0)
        protocol.armOrientationBase.setPTPCmd(PositionArm(250, 0, 0, initialAngleDefector), E_ptpMode.MOVJ_XYZ)
    protocol.ptpBase.setPtpCommonParams(50, 50)



# Mettre par defaut une zone de travail  ( le tout en bout = 200)



p1 = PositionArm(0, 0, 4, initialAngleDefector)
p_low = PositionArm(0, 0, -10, 0)
p_touch = PositionArm(0, 1, 0, 0)
p_high = PositionArm(0, -1, 10, 0)

protocol.queueCmdBase.setQueuedCmdStartExec()

# Choisir une orientation et passer sur un point intermediaire apres avoir géré acceleration
protocol.armOrientationBase.queued.setArmOrientation(True)
protocol.ptpBase.setPtpCoordinateParams(50,50,50,50)

protocol.ptpBase.queued.setPtpCommonParams(5,5)
offset0 = AngleArm(5,-5,230,initialAngleDefector)
protocol.armOrientationBase.queued.setPTPCmd(offset0,E_ptpMode.MOVJ_ANGLE)
protocol.armOrientationBase.queued.setArmOrientation(False)
print(protocol.armOrientationBase.armOrientation())
for i in range(10):
    p1.y+=2.56
    protocol.armOrientationBase.queued.setPTPCmd(p1,E_ptpMode.MOVJ_XYZ)
    # Mettre soudure sur la panne
    protocol.eioBase.queued.setDo(1, True)
    protocol.waitBase.queued.setWaitms(200)
    protocol.eioBase.queued.setDo(1, False)
    protocol.waitBase.queued.setWaitms(300)
    protocol.ptpBase.queued.setPtpCommonParams(1, 5)
    protocol.armOrientationBase.queued.setPTPCmd(p_low, E_ptpMode.MOVJ_XYZ_INC)
    protocol.armOrientationBase.queued.setPTPCmd(p_touch, E_ptpMode.MOVJ_XYZ_INC)
    protocol.eioBase.queued.setDo(1, True)
    protocol.waitBase.queued.setWaitms(2500)
    protocol.eioBase.queued.setDo(1, False)
    protocol.ptpBase.queued.setPtpCommonParams(5, 5)
    balise = protocol.armOrientationBase.queued.setPTPCmd(p_high, E_ptpMode.MOVJ_XYZ_INC)
    while (balise != protocol.queueCmdBase.queuedCmdCurrentIndex()):
        time.sleep(0.5)
pass







