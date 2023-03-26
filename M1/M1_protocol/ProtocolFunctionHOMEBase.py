from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionHOMEBase(M1_protocol):

    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setHome(self):
        msg = M1_msg.build_msg(31, True)
        return msg

    @M1_protocol.cmd
    def setHomeSwitch(self, calibrate: bool = False):
        msg = M1_msg.build_msg(33, True, self.isQueued, bytes((calibrate,)))
        return msg
