from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionHHTBase(M1_protocol):


    def __int__(self):
        super().__init__()

    def setHttTrigOutputEnabled(self,enabled:True):
        msg = M1_msg.build_msg(251, True, False, bytes((int(enabled,))))
        return msg


