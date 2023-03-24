import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionQueuedCmdBase(M1_protocol):


    def __int__(self):
        super().__init__()


    def setQueuedCmdStartExec(self):
        msg = M1_msg.build_msg(240,True)
        return msg

    def setQueuedCmdStopExec(self):
        msg = M1_msg.build_msg(241,True)
        return msg

    def setQueuedCmdForceStopExec(self):
        msg = M1_msg.build_msg(242,True)
        return msg

    def setQueuedCmdClear(self):
        msg = M1_msg.build_msg(245,True)
        return msg


    def queuedCmdCurrentIndex(self):
        msg = M1_msg.build_msg(246,True)
        return msg


    def decode_queuedCmdCurrentIndex(self,msg:bytearray) ->int:
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        count = struct.unpack("<Q",payload)
        return count

