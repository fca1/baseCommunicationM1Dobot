import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionWAITBase(M1_protocol):
    def __init__(self):
        super().__init__()



    @M1_protocol.cmd
    def setWaitms(self, sleep_ms:int):
        payload = struct.pack("<I", sleep_ms)
        return M1_msg.build_msg(110, True, self.isQueued, payload),self._decode_indexQueue
