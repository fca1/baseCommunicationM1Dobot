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
if 1:
    #protocol.homeBase.setHome()
    while protocol.status == "ran":
        time.sleep(2)
    homing_position = PositionArm(400, 0, 0)
    p0 = PositionArm(200, 0, 230) + homing_position
    p1 = PositionArm(-200, 0, 230) + homing_position
    protocol.miscBase.setUserFrame(p1, p0)  # user tool

if 0:
    pm  = Param_dynamic()
    protocol.miscBase.dynamicMotionParameter(pm)
    protocol.miscBase.setDynamicPayload(1.0)
    protocol.miscBase.setSecurityLevelConfiguration(0,0,0,0)
    protocol.miscBase.setRecoveryMode(False)

# Mettre par defaut une zone de travail  ( le tout en bout = 200)




p1 = PositionArm(0,0,4)
p2 = PositionArm(50,50,-54)



protocol.queueCmdBase.setQueuedCmdStartExec()

# Choisir une orientation et passer sur un point intermediaire apres avoir géré acceleration
protocol.armOrientationBase.queued.setArmOrientation(True)
protocol.ptpBase.setPtpCoordinateParams(50,50,50,50)

protocol.ptpBase.queued.setPtpCommonParams(100,100)
offset0 = AngleArm(60,-120,230,60)
protocol.armOrientationBase.queued.setPTPCmd(offset0,E_ptpMode.MOVJ_ANGLE)
protocol.armOrientationBase.queued.setArmOrientation(True)
print(protocol.armOrientationBase.armOrientation())
for i in range(5):
    protocol.armOrientationBase.queued.setPTPCmd(p1,E_ptpMode.MOVJ_XYZ)
    protocol.armOrientationBase.queued.setPTPCmd(p2,E_ptpMode.MOVJ_XYZ)
pass







