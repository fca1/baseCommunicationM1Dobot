from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionHHTBase(M1_protocol):


    def __init__(self):
        super().__init__()

    @M1_protocol.m1_protocol
    def setHttTrigOutputEnabled(self,enabled:True):
        msg = M1_msg.build_msg(41, True, False, bytearray((int(enabled),)))
        return msg


