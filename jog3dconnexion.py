import os
from collections import namedtuple

path_root = r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\3dconnexion\dll\x64"
os.environ["PATH"] += path_root

import pyspacemouse

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionJOGBase import E_KEY
from m1 import M1


class JogM1:
    def __init__(self, m1: M1):
        self.protocol = m1.protocol
        self.m1 = m1
        self.pt = None

    def __enter__(self):
        success = pyspacemouse.open(
            dof_callback=None, button_callback=None, button_callback_arr=None
        )
        if not success:
            raise Exception("Pb 3D connexion")
        # Se mettre en mode jog.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pyspacemouse.close()
        self.protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE, True)

        pass

    def read(self):
        factor = 2
        level_min = 0.1
        status = pyspacemouse.read()
        index = None
        Pt = namedtuple("point", ("x", "y", "z", "yaw"))
        x = int(status.x * 10) * 10
        y = int(status.y * 10) * 10
        z = int(status.z * 10) * 10
        yaw = int(status.yaw * 10) * 10
        pt = Pt(x, y, z, yaw)
        if self.pt == pt:
            return status.buttons
        print(pt)
        try:
            if abs(status.x) > level_min:
                self.protocol.jogBase.queued.setJOGCommonParams(abs(pt.x) / factor, 5)
                index = self.protocol.jogBase.queued.setJOGCmd(
                    E_KEY.YP_DOWN if pt.x > 0 else E_KEY.YN_DOWN, True
                )
                return status.buttons
            if abs(status.y) > level_min:
                self.protocol.jogBase.queued.setJOGCommonParams(abs(pt.y) / factor, 5)
                index = self.protocol.jogBase.queued.setJOGCmd(
                    E_KEY.XP_DOWN if pt.y > 0 else E_KEY.XN_DOWN, True
                )
                return status.buttons
            if abs(status.z) > level_min:
                self.protocol.jogBase.queued.setJOGCommonParams(abs(pt.z) / factor, 5)
                index = self.protocol.jogBase.queued.setJOGCmd(
                    E_KEY.ZP_DOWN if pt.z > 0 else E_KEY.ZN_DOWN, True
                )
                return status.buttons
            if abs(status.yaw) > level_min:
                self.protocol.jogBase.queued.setJOGCommonParams(abs(pt.yaw) / factor, 5)
                index = self.protocol.jogBase.queued.setJOGCmd(
                    E_KEY.RP_DOWN if pt.yaw > 0 else E_KEY.RN_DOWN, False
                )
                return status.buttons
            self.protocol.jogBase.queued.setJOGCommonParams(0, 5)
            index = self.protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE, True)
            return status.buttons
        finally:
            self.m1.wait_end_queue(index)
            self.pt = pt
            pass


if __name__ == "__main__":
    solder = M1()
    solder.setHome()
    solder.initialize_arm()

    # solder.protocol.jogBase.queued.setJOGCommonParams(10, 20)
    # index = solder.protocol.jogBase.queued.setJOGCmd(E_KEY.XN_DOWN, True)
    # index = solder.protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE, True)

    with JogM1(solder) as jog:
        while True:
            bleft, bright = jog.read()
            if bleft:
                print(solder.protocol.pos)
                break
