import time

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.M1_protocol.ProtocolFunctionJOGBase import E_KEY
from M1.misc.PositionArm import PositionArm

# Initialiser le systeme de communication udp

protocol = CommProtocolM1("192.168.0.55")
protocol.setTimeout(5)

assert protocol.serial()
# Faire un homing
protocol.hhtBase.setHttTrigOutputEnabled(False)


# Test queue
protocol.queueCmdBase.setQueuedCmdForceStopExec()
protocol.queueCmdBase.setQueuedCmdClear()
for i in range(30):
    print(protocol.armOrientationBase.queued.setArmOrientation(False))
step0 = protocol.jogBase.queued.setJOGCmd(E_KEY.XN_DOWN,isJoint=False)
protocol.waitBase.queued.setWaitms(1000)
step1 = protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE,isJoint=False)
protocol.queueCmdBase.setQueuedCmdStartExec()
time.sleep(1)
step2  = protocol.queueCmdBase.queuedCmdCurrentIndex()



if 0:
    protocol.homeBase.setHome()
    while protocol.status == "ran":
        time.sleep(2)
    p0 = PositionArm(0, 0, 230)
    p1 = PositionArm(400, 0, 230)
    protocol.miscBase.setUserFrame(p0, p1)  # user tool
    pinitial = p1 - p0
    pass





# Test sur user position
p0 = PositionArm(400, 0, 230)
p1 = PositionArm(200, 0, 230)
protocol.miscBase.setUserFrame(p0, p1)  # user tool

protocol.armOrientationBase.queued.setArmOrientation(False)
p0, _ = protocol.pos
pr = PositionArm(100, 0, -30, 0)
protocol.armOrientationBase.setPTPCmd(pr, E_ptpMode.MOVL_XYZ)

protocol.alarmBase.clearAllAlarmsState()
# Le systeme est communiquant.
# Couper les moteurs pour faire du teaching
protocol.hhtBase.setHttTrigOutputEnabled(True)
# Attendre le retour de P0,P1
# input("Se positionner en P0")
p0, _ = protocol.pos
# input("Se positionner en P1")
p1, _ = protocol.pos
protocol.miscBase.setUserFrame(p0, p1)  # user tool
protocol.miscBase.setToolFrame(0, 0, 0)  # user tool
# Demander une orientation de l'arm
protocol.armOrientationBase.setArmOrientation(right=False)
# Se remettre en mode normal
protocol.hhtBase.setHttTrigOutputEnabled(False)
# Acceleration a 100%
protocol.ptpBase.setPtpCommonParams(velocity=10, acceleration=100)
# Revenir en p0
protocol.armOrientationBase.setPTPCmd(p0)
time.sleep(6)
protocol.armOrientationBase.setPTPCmd(p1)
time.sleep(6)
