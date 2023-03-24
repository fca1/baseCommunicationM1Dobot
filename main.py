from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol import ProtocolFunctionArmOrientationBase
from M1.M1_protocol.ProtocolFunction import ProtocolFunction
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode

comm = M1_comm_udp("192.168.0.55")

protocol = ProtocolFunction(comm)

serial = protocol.serial()
protocol.setClearAllAlarmsState()
status = protocol.status_ok

pos, angle = protocol.pos()

comm.cmd(protocol.armOrientationBase.setPTPCmd, None, 0, 0, 100, 20)
msg = ProtocolFunctionArmOrientationBase.setPTPCmd(-172, 50, -165, 100, mode=E_ptpMode.MOVJ_XYZ)
