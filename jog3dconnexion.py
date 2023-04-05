import os
import pyspacemouse

from M1.CommProtocolM1 import CommProtocolM1
from M1.M1_protocol.ProtocolFunctionJOGBase import E_KEY
from soldering import Soldering


class JogM1:
    def __init__(self,protocol:CommProtocolM1):
        self.protocol = protocol
        path_root = r";C:\Users\frant\PycharmProjects\3dconnexion\dll\x64"
        os.environ['PATH'] += path_root

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
        status =  pyspacemouse.read()
        if status.x:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.x)*factor*100,20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.YP_DOWN if status.x >0 else E_KEY.YN_DOWN,True)
            return
        if status.y:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.y)*factor*100,20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.XP_DOWN if status.y >0 else E_KEY.XN_DOWN,True)
            return
        if status.z:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.z)*factor*100,20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.ZP_DOWN if status.z >0 else E_KEY.ZN_DOWN,True)
            return
        if status.yaw:
            self.protocol.jogBase.queued.setJOGCommonParams(abs(status.yaw) * factor * 100, 20)
            self.protocol.jogBase.queued.setJOGCmd(E_KEY.RP_DOWN if status.z > 0 else E_KEY.RN_DOWN, False)
            return
        self.protocol.jogBase.queued.setJOGCmd(E_KEY.IDLE, True)
        return status.buttons


if __name__ == '__main__':
    solder = Soldering()
    with JogM1(solder.protocol) as jog:
        while True:
            bleft,bright = jog.read()
            if bleft:
                print(solder.protocol.pos)
                break






