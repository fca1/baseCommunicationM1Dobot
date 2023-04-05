import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol



# uint8_t address; // EIO address: If mode is set to 0, the value range is 1 to 24. If mode is set to 1,
# the value range is 1 to 6
# uint8_t mode; // Triggering mode. 0: Level trigger.1:A/D trigger
# uint8_t condition; // Triggering condition
# Level: 0, equal. 1, unequal
# A/D: 0, less than. 1,less than or equal
# 2, greater than or equal. 3, greater than
# uint16_t threshold;


class ProtocolFunctionTRIGBase(M1_protocol):
    def __init__(self):
        super().__init__()



@M1_protocol.cmd
def setTrigCmd(self,nber_io:int,level:bool):
    assert 0<nber_io<=24
    datas = struct.pack('<BBBH', nber_io, 0, 0,level)
    msg = M1_msg.build_msg(120, True, self.isQueued, datas)
    return msg, self._decode_indexQueue

