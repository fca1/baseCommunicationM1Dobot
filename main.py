import time

from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol import ProtocolFunctionArmOrientationBase
from M1.M1_protocol.ProtocolFunction import ProtocolFunction
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm

# Initialiser le systeme de communication udp
Pinitial = PositionArm(400,0,0,0)
comm = M1_comm_udp("192.168.0.55")
protocol = ProtocolFunction(comm)
assert protocol.serial()
# Faire un homing
comm.send_msg(protocol.hhtBase.setHttTrigOutputEnabled(True))
comm.send_msg(protocol.homeBase.setHome())
Pinitial =protocol.pos

comm.send_msg(protocol.alarmBase.clearAllAlarmsState())
# Le systeme est communiquant.
# Couper les moteurs pour faire du teaching
comm.send_msg(protocol.hhtBase.setHttTrigOutputEnabled(True))
# Attendre le retour de P0,P1
#input("Se positionner en P0")
p0, _ = protocol.pos
#input("Se positionner en P1")
p1, _ = protocol.pos
comm.send_msg(protocol.miscBase.setUserFrame(p0,p1))  # user tool
comm.send_msg(protocol.miscBase.setToolFrame(0,0,0))  # user tool
# Demander une orientation de l'arm
comm.send_msg(protocol.armOrientationBase.setArmOrientation(right=False))
# Se remettre en mode normal
comm.send_msg(protocol.hhtBase.setHttTrigOutputEnabled(False))
# Acceleration a 100%
comm.send_msg(protocol.ptpBase.setPtpCommonParams(velocity=10,acceleration=100))
# Revenir en p0
comm.send_msg(protocol.armOrientationBase.setPTPCmd(p0))
time.sleep(6)
comm.send_msg(protocol.armOrientationBase.setPTPCmd(p1))
time.sleep(6)








