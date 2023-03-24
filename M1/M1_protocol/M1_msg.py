import struct


class M1_msg:
    """
    Le dobot M1 utilise le protocole @see 'Dobot M1 Communication Protocol'.
    L'octet de controle n'indique pas s'il s'agit de bits ( rw et isQueued), dans le code bit1 et bit0
    """

    @staticmethod
    def _build_msg(payload: bytearray) -> bytearray:
        length = len(payload)
        chksum = -sum(payload) & 0xFF
        msg = bytearray((0xAA, 0xAA, length, *payload, chksum))
        return msg

    @staticmethod
    def _build_payload(_id: int, write: bool = False, isQueued: bool = False, *params):
        assert _id < 256
        ctrl = (1 if write else 0) << 1 + (1 if isQueued else 0)
        payload = bytearray((_id, ctrl, *params))
        return payload

    @staticmethod
    def build_msg(_id: int, write: bool = False, isQueued: bool = False, *params) -> bytearray:
        payload = M1_msg._build_payload(_id, write, isQueued, *params)
        return M1_msg._build_msg(payload)

    @staticmethod
    def decode_msg(msg: bytearray) -> (int, int, bool, bytearray):
        he1, he2, length = struct.unpack("BBB", msg[0:3])
        if (he1, he2) != (0xAA, 0xAA):
            raise Exception("bad header")
        _id, ctrl = struct.unpack("BB", msg[3:5])
        length -= 2
        payload_wchk = msg[5:]
        chk = payload_wchk[-1]
        payload = payload_wchk[0:-1]
        if len(payload) != length:
            raise Exception("bad length")
        if -(sum(payload)+_id+ctrl) & 0xff != chk:
            raise Exception("bad chk")
        return _id, (ctrl & 0x02) >> 1, bool(ctrl & 0x01), payload
