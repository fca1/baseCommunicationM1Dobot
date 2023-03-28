import struct
from typing import Tuple, Any

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionQueuedCmdBase(M1_protocol):

    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setQueuedCmdStartExec(self):
        msg = M1_msg.build_msg(240, True)
        return msg

    @M1_protocol.cmd
    def setQueuedCmdStopExec(self):
        msg = M1_msg.build_msg(241, True)
        return msg

    @M1_protocol.cmd
    def setQueuedCmdForceStopExec(self):
        msg = M1_msg.build_msg(242, True)
        return msg

    @M1_protocol.cmd
    def setQueuedCmdClear(self):
        msg = M1_msg.build_msg(245, True)
        return msg

    @M1_protocol.cmd
    def queuedCmdCurrentIndex(self):
        msg = M1_msg.build_msg(246)
        return msg, self._decode_queuedCmdCurrentIndex

    def _decode_queuedCmdCurrentIndex(self, msg: bytearray) -> tuple[Any, ...]:
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        count = struct.unpack("<Q", payload)
        return count
