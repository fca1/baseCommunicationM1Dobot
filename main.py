import socket

from M1.M1_communication.M1_comm_udp import M1_comm_udp
from M1.M1_protocol import ProtocolFunctionArmOrientationBase
from M1.M1_protocol import ProtocolFunctionDeviceInfoBase
from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode

msg = ProtocolFunctionArmOrientationBase.setPTPCmd(-172,50,-165,100,mode=E_ptpMode.MOVJ_XYZ)


comm = M1_comm_udp("192.168.0.55")
bytesToSend = ProtocolFunctionDeviceInfoBase.deviceSN()
answer = comm.send_msg(bytesToSend)
ProtocolFunctionDeviceInfoBase.decode_deviceSN(answer)
print(answer)

