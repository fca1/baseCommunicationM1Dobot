import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionEIOBase(M1_protocol):
    # @TODO problem with documentation, impossible to retrieve the status of IO
    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def do(self):
        msg = M1_msg.build_msg(131, False, self.isQueued)
        return msg, self._decode_do

    @M1_protocol.cmd
    def setDo(self, index: int, enable: bool):
        assert 1 <= index <= 22
        msg = M1_msg.build_msg(
            131, True, self.isQueued, bytes((int(index), int(enable)))
        )
        return msg, self._decode_indexQueue

    def _decode_do(self, msg) -> bool:
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        return bool(payload[1])

    @M1_protocol.cmd
    def di(self, index: int):
        payload = struct.pack("<ff", index, 0)
        msg = M1_msg.build_msg(133, False, False, payload)
        return msg, self._decode_di

    def _decode_di(self, msg) -> (int, bool):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        return payload
