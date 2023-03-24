from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.ProtocolFunction import ProtocolFunction


class ProtocolFunctionDeviceInfoBase(ProtocolFunction):


    def __int__(self):
        super().__init__()


    def deviceSN(self):
        msg = M1_msg.build_msg(0x00)
        return msg


    def decode_deviceSN(self,msg:bytearray):
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        return str(payload[:-1])
        pass
