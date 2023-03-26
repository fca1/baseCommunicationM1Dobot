import struct

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol


class ProtocolFunctionALARMBase(M1_protocol):

    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def clearAllAlarmsState(self):
        msg = M1_msg.build_msg(20, True)
        return msg

    @M1_protocol.cmd
    def status(self):
        return M1_msg.build_msg(29), self.decode_status

    def decode_status(self, msg):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        st0, st1, _, _ = struct.unpack("BBBB", payload)
        if st0 & 1:
            return "error"
        if st1 & 1:
            return "collision"
        if st0 & 2:
            return "stopped"
        if st0 & 8:
            return "ran"

        return ""
