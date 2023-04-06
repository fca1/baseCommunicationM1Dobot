import time

from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm
from m1 import M1


class SolderEcolow(M1):
    # en mm
    # Les signes negatifs sont pour le deplacement (selon x+ et y+)
    # Dans le cas présent, la longueur la plus grande du PCB est Y.
    # Description du PCB
    MATRIX_CONNECTORS=(2,5)
    DIST_BETWEEN_CNX_X =-72
    DIST_BETWEEN_CNX_Y=45.65
    # description du connexteur
    MATRIX_INSIDE_CONNECTOR=(3,2)
    DIST_BETWEEN_PINS_X=-4.56
    DIST_BETWEEN_PINS_Y =9.12
    HEIGHT_PIN_SECURITY=5   # hauteur relative par rapport au PCB

    OUTPUT_CMD_DISTRIBUTE=1 # Commande pour demander soudure au distributeur
    INPUT_CMD_DISTRIBUTE=1

    # En passant par la fonction JUMP, il est possible de pouvoir choisir 2 planchers.
    # Plancher interdisant de varier (X,Y)
    DEFECTOR_LENGTH = 45



    def __init__(self,ip_addr="192.168.0.55",home=False):
        super().__init__(ip_addr=ip_addr)
        self.heigth_pcb = 100       # doit etre choisi.
        self.clean_solder = PositionArm(350,-350,200)   # @TODO initialiser avec valeur
        self.initialize_origin()
        if home:
            self.home()
        self.initialize_arm()
        self.initialize_length_defector(self.DEFECTOR_LENGTH)
        self._configure_jumpJ()
        pass


    def _configure_jumpJ(self):
        # 2 plafonds sont prévus et mesurés. (la hauteur de securite et celle de déplacement)
        # Par rapport à la hauteur du PCB, monter l'outil de la sécurité avant d'avoir le droit de bouger en x,y
        # Le plafond étant à la meme hauteur max, pas de variation en Z pendant le déplacement.
        self.protocol.ptpBase.setPtpJumpParams(self.HEIGHT_PIN_SECURITY,self.heigth_pcb+self.HEIGHT_PIN_SECURITY)
        pass




    def cycle_solder_pins(self,initial_point:PositionArm):
        positions = set()
        for x in range(self.MATRIX_INSIDE_CONNECTOR[0]):
            for y in range(self.MATRIX_INSIDE_CONNECTOR[1]):
                point = initial_point.copy()
                point.x+=x*self.DIST_BETWEEN_PINS_X
                point.y += y * self.DIST_BETWEEN_PINS_Y
                positions.add(point)

        while positions:
            current = self.pos
            point = sorted(positions, key=current.distance)[0]
            positions.remove(point)
            self.protocol.ptpBase.queued.setPtpCommonParams(5, 5)
            self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
            self.cycle_solder_pin(point)
        pass


    def cycle_solder_board(self,origin_connector:PositionArm):
        positions = set()
        for x in range(self.MATRIX_CONNECTORS[0]):
            for y in range(self.MATRIX_CONNECTORS[1]):
                # positionner la tete
                point = origin_connector.copy()
                point.x+=x*self.DIST_BETWEEN_CNX_X
                point.y += y * self.DIST_BETWEEN_CNX_Y
                positions.add(point)
        # positions contient toutes les positions en attente;
        while positions:
            current = self.pos
            point = sorted(positions,key=current.distance)[0]
            positions.remove(point)
            self.protocol.ptpBase.queued.setPtpCommonParams(50, 50)
            self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
            self.cycle_solder_pins(point)
        pass


    def _cycle_solder_distribute(self,is_short:int=0):
        self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,1)
        self.protocol.waitBase.queued.setWaitms(300 if is_short else is_short)
        self.wait_end_queue(self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,0))


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
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
        time.sleep(1)   # chauffer
        self._cycle_solder_distribute() # Mettre de la soudure sur le fer
        time.sleep(3)       # laisser la soudure
        point.z = self.heigth_pcb+self.HEIGHT_PIN_SECURITY
        self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ))

    def cycle_clean_solder(self):
        # faire un cycle de nettoyage
        point = self.clean_solder.copy()
        low_ = PositionArm(0,0,-20,0)
        high_ = PositionArm(0,0,-low_.z,0)
        self.protocol.ptpBase.queued.setPtpCommonParams(50, 50)
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
        self.protocol.ptpBase.queued.setPtpCommonParams(10, 10)
        for i in range(5):
            self.protocol.armOrientationBase.queued.setPTPCmd(low_, E_ptpMode.JUMP_XYZ_INC)
            self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(high_, E_ptpMode.JUMP_XYZ_INC))
        pass




    def start_cycle(self):
        pass


if __name__ == '__main__':
    solder = SolderEcolow(home=False)
    #solder.cycle_clean_solder()
    origin_connector = PositionArm(273, -311, solder.heigth_pcb+solder.HEIGHT_PIN_SECURITY)  # @TODO initialiser avec valeur
    solder.cycle_solder_board(origin_connector)
    pass