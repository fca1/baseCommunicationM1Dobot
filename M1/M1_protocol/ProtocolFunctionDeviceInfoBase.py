from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionDeviceInfoBase(M1_protocol):


    def __int__(self):
        super().__init__()

    def build_commands(self):
        return {
            "deviceSn" : ( self.deviceSn,self.decode_deviceSN)
        }

    def deviceSN(self):
        msg = M1_msg.build_msg(0x00)
        return msg


    def decode_deviceSN(self,msg:bytearray):
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        return payload[:-1].decode()
        pass
