from M1.M1_protocol.M1_msg import M1_msg


class ProtocolFunctionHOMEBase():


    def __int__(self):
        super().__init__()


    def setHome(self):
        msg = M1_msg.build_msg(31,True)
        return msg



