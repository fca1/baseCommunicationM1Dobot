import os

path_root = r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\3dconnexion\dll\x64"
os.environ['PATH'] += path_root

import pyspacemouse

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionJOGBase import E_KEY
from m1 import M1


class JogM1:
    def __init__(self,protocol:CommProtocolM1):
        self.protocol = protocol

    def __enter__(self):
        success = pyspacemouse.open(dof_callback=None, button_callback=None,
                                    button_callback_arr=None)
        if not success:
            raise Exception("Pb 3D connexion")
        # Se mettre en mode jog.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pyspacemouse.close()
        self.protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE,True)
        pass

    def read(self):
        factor = 0.2
        level_min = 0.1
        status =  pyspacemouse.read()
        if abs(status.x)>level_min:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.x)*factor*100,20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.YP_DOWN if status.x >0 else E_KEY.YN_DOWN,True)
            return
        if abs(status.y)>level_min:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.y)*factor*100,20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.XP_DOWN if status.y >0 else E_KEY.XN_DOWN,True)
            return
        if abs(status.z)>level_min:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.z)*factor*100,20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.ZP_DOWN if status.z >0 else E_KEY.ZN_DOWN,True)
            return
        if abs(status.yaw)>level_min:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.yaw) * factor * 100, 20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.RP_DOWN if status.z > 0 else E_KEY.RN_DOWN, False)
            return
        self.protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE, True)
        return status.buttons


if __name__ == '__main__':
    solder = M1()
    solder.home()
    solder.initialize_arm()
    with JogM1(solder.protocol) as jog:
        while True:
            bleft,bright = jog.read()
            if bleft:
                print(solder.protocol.pos)
                break






