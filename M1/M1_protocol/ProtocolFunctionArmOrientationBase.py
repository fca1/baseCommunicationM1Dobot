import struct
from enum import Enum, unique

from M1.M1_protocol.M1_msg import M1_msg
from M1.M1_protocol.M1_protocol import M1_protocol
from M1.misc.AngleArm import AngleArm
from M1.misc.PositionArm import PositionArm


@unique
class E_ptpMode(Enum):
    JUMP_XYZ = (
        0  # JUMP mode, (x,y,z,r) is the target point in Cartesian coordinate system
    )
    MOVJ_XYZ = (
        1  # MOVJ mode, (x,y,z,r) is the target point in Cartesian coordinate system
    )
    MOVL_XYZ = (
        2  # MOVL mode, (x,y,z,r) is the target point in Cartesian coordinate system
    )
    JUMP_ANGLE = (
        3  # JUMP mode, (x,y,z,r) is the target point in Joint coordinate system
    )
    MOVJ_ANGLE = (
        4  # MOVJ mode, (x,y,z,r) is the target point in Joint coordinate system
    )
    MOVL_ANGLE = (
        5  # MOVL mode, (x,y,z,r) is the target point in Joint coordinate system
    )
    MOVJ_INC = (
        6  # MOVJ mode, (x,y,z,r) is the angle increment in Joint coordinate system
    )
    MOVL_INC = 7  # MOVL mode, (x,y,z,r) is the Cartesian coordinate increment in Joint coordinate system
    MOVJ_XYZ_INC = 8  # MOVJ mode, (x,y,z,r) is the Cartesian coordinate increment in Cartesian coordinate system
    JUMP_MOVL_XYZ = 9  # JUMP mode, (x,y,z,r) is the Cartesian coordinate increment in Cartesian coordinate system


class ProtocolFunctionArmOrientationBase(M1_protocol):
    def __init__(self):
        super().__init__()

    @M1_protocol.cmd
    def setPTPCmd(
        self, pos: [PositionArm or AngleArm], mode: E_ptpMode = E_ptpMode.MOVJ_XYZ
    ) -> bytearray:
        # "aa aa 13 54 03 01 (00 00 2c c3) (00 00 48 42) (00 00 00 10)   25 c3 00 00 c8 42 3d"
        if mode in (
            E_ptpMode.JUMP_XYZ,
            E_ptpMode.MOVJ_XYZ,
            E_ptpMode.MOVL_XYZ,
            E_ptpMode.MOVJ_XYZ_INC,
            E_ptpMode.JUMP_MOVL_XYZ,
        ):
            datas = struct.pack("<Bffff", mode.value, pos.x, pos.y, pos.z, pos.r)
        else:
            datas = struct.pack(
                "<Bffff", mode.value, pos.base, pos.rear, pos.front, pos.defector
            )
        msg = M1_msg.build_msg(84, True, self.isQueued, datas)
        return msg, self._decode_indexQueue

    @M1_protocol.cmd
    def setArmOrientation(self, right: bool):
        return (
            M1_msg.build_msg(50, True, self.isQueued, bytearray((int(right),))),
            self._decode_indexQueue,
        )

    @M1_protocol.cmd
    def armOrientation(self):
        return M1_msg.build_msg(50), self._decode_orientation

    def _decode_orientation(self, msg):
        _id, write, isqueued, payload = M1_msg.decode_msg(msg)
        return "right" if payload[0] else "left"
