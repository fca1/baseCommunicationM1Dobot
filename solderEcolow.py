import time

from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm
from soldering import Soldering


class SolderEcolow(Soldering):
    # en mm
    MATRIX_CONNECTORS=(5,2)
    DIST_BETWEEN_CNX_X=45.65
    DIST_BETWEEN_CNX_Y =72
    MATRIX_INSIDE_CONNECTOR=(3,2)
    DIST_BETWEEN_PINS_X=4.56
    DIST_BETWEEN_PINS_Y =9.12
    HEIGHT_PIN_SECURITY=3
    OUTPUT_CMD_DISTRIBUTE=1
    INPUT_CMD_DISTRIBUTE=1



    def __init__(self,ip_addr="192.168.0.55"):
        super().__init__(ip_addr=ip_addr)
        self.heigth_pcb = 100       # doit etre choisi.
        self.origin_connector = PositionArm(100,100,self.heigth_pcb)   # @TODO initialiser avec valeur
        self.clean_solder = PositionArm(-100,-100,200)   # @TODO initialiser avec valeur
        self.place_to_home()
        self.initialize_arm()
        self._configure_jumpJ()
        pass


    def _configure_jumpJ(self):
        # 2 plafonds sont prévus et mesurés. (la hauteur de securite et celle de déplacement)
        self.protocol.ptpBase.queued.setPtpJumpParams(self.heigth_pcb+self.HEIGHT_PIN_SECURITY,self.heigth_pcb+2*self.HEIGHT_PIN_SECURITY)




    def cycle_solder_pins(self,initial_point:PositionArm):
        for x in range(self.MATRIX_INSIDE_CONNECTOR[0]):
            for y in range(self.MATRIX_INSIDE_CONNECTOR[1]):
                point = initial_point.copy()
                point.x+=x*self.DIST_BETWEEN_PINS_X
                point.y += y * self.DIST_BETWEEN_PINS_Y
                self.protocol.ptpBase.queued.setPtpCommonParams(5, 5)
                self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
                self.cycle_solder_pin(point)
        pass


    def cycle_solder_board(self,origin_connector:PositionArm):
        for x in range(self.MATRIX_CONNECTORS[0]):
            for y in range(self.MATRIX_CONNECTORS[1]):
                # positionner la tete
                point = origin_connector.copy()
                point.x+=x*self.DIST_BETWEEN_CNX_X
                point.y += y * self.DIST_BETWEEN_CNX_Y
                self.protocol.ptpBase.queued.setPtpCommonParams(50, 50)
                self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
                self.cycle_solder_pins(point)
        pass


    def _cycle_solder_distribute(self,is_short:int=0):
        self.protocol.eioBase.setDo(self.OUTPUT_CMD_DISTRIBUTE,1)
        time.sleep(0.300 if is_short else is_short)
        self.protocol.eioBase.setDo(self.OUTPUT_CMD_DISTRIBUTE, 0)


    def cycle_solder_pin(self,initial_point:PositionArm):
        """
        Le pointe a souder est en hauteur à 1mm en Y
        :return:
        """
        self.protocol.ptpBase.queued.setPtpCommonParams(1, 5)
        point = initial_point.copy()
        point.z = self.heigth_pcb
        self._cycle_solder_distribute() # Mettre de la soudure sur le fer
        time.sleep(0.5)
        # Mettre en position soudage
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
        time.sleep(1)   # chauffer
        self._cycle_solder_distribute() # Mettre de la soudure sur le fer
        time.sleep(3)       # laisser la soudure
        point.z = self.heigth_pcb+self.MAX_HEIGHT
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)

    def cycle_clean_solder(self):
        # faire un cycle de nettoyage
        point = self.clean_solder.copy()
        low_ = PositionArm(0,0,-20,0)
        high_ = PositionArm(0,0,-low_.z,0)
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
        self.protocol.armOrientationBase.queued.setPTPCmd(low_, E_ptpMode.MOVJ_XYZ_INC)
        self.protocol.armOrientationBase.queued.setPTPCmd(high_, E_ptpMode.MOVJ_XYZ_INC)




    def start_cycle(self):
        pass


if __name__ == '__main__':
    solder = SolderEcolow()
    solder.cycle_clean_solder()
    pass