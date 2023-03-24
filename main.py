import time

from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol import ProtocolFunctionArmOrientationBase
from M1.M1_protocol.ProtocolFunction import ProtocolFunction
from M1.M1_protocol.ProtocolFunctionALARMBase import setClearAllAlarmsState
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode

# Initialiser le systeme de communication udp
comm = M1_comm_udp("192.168.0.55")
protocol = ProtocolFunction(comm)
assert protocol.serial()

# Le systeme est communiquant.
# Couper les moteurs pour faire du teaching
comm.send_msg(protocol.hhtBase.setHttTrigOutputEnabled(True))
# Attendre le retour de P0,P1
input("Se positionner en P0")
p0, _ = protocol.pos()
input("Se positionner en P1")
p1, _ = protocol.pos()
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









setClearAllAlarmsState(protocol.comm, protocol.alarmBase)
status = protocol.status_ok

pos, angle = protocol.pos()

comm.cmd(protocol.armOrientationBase.setPTPCmd, None, 0, 0, 100, 20)
msg = ProtocolFunctionArmOrientationBase.setPTPCmd(-172, 50, -165, 100, mode=E_ptpMode.MOVJ_XYZ)
