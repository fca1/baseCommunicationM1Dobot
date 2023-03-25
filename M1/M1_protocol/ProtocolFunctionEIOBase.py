from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionEIOBase(M1_protocol):
    def __init__(self):
        super().__init__()

    def do(self):
        msg = M1_msg.build_msg(131,self.isQueued)
        return msg,self.decode_do

    def setDo(self,index:bool,enable:bool):
        msg = M1_msg.build_msg(131, self.isQueued,bytes((int(index),int(enable))))
        return msg,self.decode_indexQueue

    def decode_do(self,msg) -> bool:
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        return bool(payload[1])

