from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionEIOBase(M1_protocol):
    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def do(self):
        msg = M1_msg.build_msg(131, self.isQueued)
        return msg, self._decode_do

    @M1_protocol.cmd
    def setDo(self, index: int, enable: bool):
        assert 1 <= index <=22
        msg = M1_msg.build_msg(131,True, self.isQueued, bytes((int(index), int(enable))))
        return msg, self._decode_indexQueue

    def _decode_do(self, msg) -> bool:
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        return bool(payload[1])
