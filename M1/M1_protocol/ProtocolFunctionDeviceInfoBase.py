from M1.M1_protocol.M1_msg import M1_msg


class ProtocolFunctionDeviceInfoBase(M1_protocol):


    def __int__(self):
        super().__init__()


    def deviceSN(self):
        msg = M1_msg.build_msg(0x00)
        return msg


    def decode_deviceSN(self,msg:bytearray):
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        return payload[:-1].decode()
        pass
