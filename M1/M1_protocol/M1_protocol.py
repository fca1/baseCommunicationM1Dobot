import struct

from M1.M1_protocol.M1_msg import M1_msg


class M1_protocol:

    def __int__(self):
        self.isQueued=False


    def decode_indexQueue(self,msg) ->int:
        id,write,isqueued,payload =M1_msg.decode_msg(msg)
        count = struct.unpack("<Q",payload)
        return count


    pass
