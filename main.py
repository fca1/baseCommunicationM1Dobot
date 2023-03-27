import time

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.M1_protocol.ProtocolFunctionJOGBase import E_KEY
from M1.misc.PositionArm import PositionArm

# Initialiser le systeme de communication udp

protocol = CommProtocolM1("192.168.0.55")
protocol.setTimeout(5)

# Detection presence du M1
assert protocol.serial()

# Mettre alimentation sur le robot
protocol.hhtBase.setHttTrigOutputEnabled(False)
# Pas d'impulsion sur la sortie
protocol.eioBase.setDo(1,False)



reason = protocol.alarm
if reason:
    print(f"Erreur sur le M1: error ={reason}")
    protocol.alarmBase.clearAllAlarmsState()

# Nettoyer la queue de messages
protocol.queueCmdBase.setQueuedCmdForceStopExec()
protocol.queueCmdBase.setQueuedCmdClear()

# Faire un homing (Attention R ? )
protocol.homeBase.setHome()
while protocol.status == "ran":
    time.sleep(2)

# Mettre par defaut une zone de travail  ( le tout en bout = 0)
p0 = PositionArm(0, 0, 230)
p1 = PositionArm(400, 0, 230)
protocol.miscBase.setUserFrame(p0, p1)  # user tool

# Choisir une orientation et passer sur un point intermediaire apres avoir géré acceleration
protocol.armOrientationBase.queued.setArmOrientation(False)
protocol.ptpBase.setPtpCoordinateParams(50,50,50,50)

p1 = PositionArm(200,100,200)
p2 = PositionArm(150,150,150)

while True:
    protocol.armOrientationBase.setPTPCmd(p1,E_ptpMode.MOVL_XYZ)
    protocol.armOrientationBase.setPTPCmd(p2,E_ptpMode.MOVL_XYZ)







