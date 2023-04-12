import logging
import sys
import time

from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm
from m1 import M1
from solder_distribute.simplepyble_dir.syncBleOrderDistrib import BleOrderDistrib


class SolderEcolow(M1):
    ALTITUDE_PCB=49
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
    
    OUTPUT_CMD_DISTRIBUTE=18 # Commande pour demander soudure au distributeur (mode pas ble)
    INPUT_CMD_DISTRIBUTE=20  # Attente triggger suite ordre par BLE ou commande relay

    # Une grille est au dessus du PCB avec une epaisseur de 10mm, cette variable permet de passer cette grille
    HEIGHT_SHAPE = 20

    # En passant par la fonction JUMP, il est possible de pouvoir choisir 2 planchers.
    # Plancher interdisant de varier (X,Y)
    DEFECTOR_LENGTH = 45


    
    def __init__(self,ip_addr="192.168.0.55",home=False):
        # Communication avec le dobot M1
        super().__init__(ip_addr=ip_addr)
        self.distrib = BleOrderDistrib()


        # Le pot de nettoyage du fer a souder 
        self.clean_solder = PositionArm(100,0,70)   #


        self.initialize()

        if home:
            self.home()
        # Gestion des hauteurs de securité
        self._configure_jumpJ()
        pass

    def initialize(self):
        try:
            self.initialize_origin()
            self._init_io()
            self.initialize_arm()           # Choix gauche ou droit
            self.initialize_length_defector(self.DEFECTOR_LENGTH)
            self.distrib.scan_and_connect() # La connextion BLE est faite une fois pour toute.
        except Exception as e:
            logging.error(e)
            sys.exit(1)





    def _init_io(self):
        # stopper distri

        self.protocol.eioBase.setDo(self.OUTPUT_CMD_DISTRIBUTE,0)
        pass

    def _configure_jumpJ(self):
        # 2 plafonds sont prévus et mesurés. (la hauteur de securite et celle de déplacement)
        # Par rapport à la hauteur du PCB, monter l'outil de la sécurité avant d'avoir le droit de bouger en x,y
        # Le plafond étant à la meme hauteur max, pas de variation en Z pendant le déplacement.
        self.protocol.ptpBase.setPtpJumpParams(self.HEIGHT_PIN_SECURITY,self.ALTITUDE_PCB+self.HEIGHT_SHAPE)
        pass




    def cycle_solder_pins(self,initial_point:PositionArm):

        positions = set()
        for x in range(self.MATRIX_INSIDE_CONNECTOR[0]):
            for y in range(self.MATRIX_INSIDE_CONNECTOR[1]):
                point = initial_point.copy()
                point.x+=x*self.DIST_BETWEEN_PINS_X
                point.y += y * self.DIST_BETWEEN_PINS_Y
                point.z = self.ALTITUDE_PCB+self.HEIGHT_PIN_SECURITY
                positions.add(point)

        while positions:
            current = self.pos
            point = sorted(positions, key=current.distance)[0]
            positions.remove(point)
            self.protocol.ptpBase.queued.setPtpCommonParams(5, 5)
            self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
            self.cycle_solder_pin(point)
            pass
        pass


    def cycle_solder_board(self,origin_connector:PositionArm,x0:int=None,y0:int=None,disable=False)  :
        positions = set()
        assert x0 is None or 0<=x0<self.MATRIX_CONNECTORS[0]
        assert y0 is None or 0 <= y0 < self.MATRIX_CONNECTORS[1]

        for x in range(self.MATRIX_CONNECTORS[0]):
            for y in range(self.MATRIX_CONNECTORS[1]):
                if x0 is not None and x!= x0:
                    continue
                if y0 is not None and y!= y0:
                    continue
                # positionner la tete
                point = origin_connector.copy()
                point.x+=x*self.DIST_BETWEEN_CNX_X
                point.y += y * self.DIST_BETWEEN_CNX_Y
                point.z = self.ALTITUDE_PCB+self.HEIGHT_PIN_SECURITY
                positions.add(point)
        # positions contient toutes les positions en attente;
        if disable: # pour debug ou connaitre les points
            return positions
        while positions:
            current = self.pos
            point = sorted(positions,key=current.distance)[0]
            positions.remove(point)
            self.protocol.ptpBase.queued.setPtpCommonParams(20, 20)
            # En mode jump, l'altitude de déplacement est SHAPE
            self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ))
            self.cycle_solder_pins(point)
        pass


    def _cycle_solder_distribute(self,is_short:int=0) -> None:
        # La distribution se fait via ble
        # self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,1)
        # self.protocol.waitBase.queued.setWaitms(300 if is_short else is_short)
        # self.wait_end_queue(self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,0))
        time.sleep(2)
        if not self.distrib.distribute(100,1500,-100,200,timeout_ms=1500):
            logging.error("Probleme de distribution de soudure")
        time.sleep(2)






    def cycle_solder_pin(self,initial_point:PositionArm) -> None:
        """
        Le pointe a souder est en hauteur à 1mm en Y
        :return:
        """
        self.protocol.ptpBase.queued.setPtpCommonParams(1, 5)
        point = initial_point.copy()
        point.z = self.ALTITUDE_PCB
        #self._cycle_solder_distribute() # Mettre de la soudure sur le fer
        #time.sleep(2)
        # Mettre en position soudage
        try:
            self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ))
            self._cycle_solder_distribute() # Mettre de la soudure sur le fer
        finally:
            point.z = self.ALTITUDE_PCB+self.HEIGHT_PIN_SECURITY
            self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ))
        pass

    def cycle_clean_solder(self) -> None:
        # faire un cycle de nettoyage
        point = self.clean_solder.copy()
        point.r=self.pos.r
        low_ = PositionArm(0,0,-20,0)
        high_ = PositionArm(0,0,-low_.z,0)
        self._cycle_solder_distribute()
        self.protocol.ptpBase.queued.setPtpCommonParams(20, 20)
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
        self.protocol.ptpBase.queued.setPtpCommonParams(10, 10)
        for i in range(3):
            self.protocol.armOrientationBase.queued.setPTPCmd(low_, E_ptpMode.MOVJ_XYZ_INC)
            self.protocol.armOrientationBase.queued.setPTPCmd(high_, E_ptpMode.MOVJ_XYZ_INC)
        self.home()
        pass




    def start_cycle(self):
        pass

def place_cnx_00():
    solder = SolderEcolow(home=True)
    origin_connector = PositionArm(316.8, -315.2, solder.ALTITUDE_PCB)  # @TODO initialiser avec valeur
    # Verifier la position
    positionCnx00 = solder.cycle_solder_board(origin_connector, 0, 0,disable=True).pop()
    solder.wait_end_queue(solder.protocol.armOrientationBase.queued.setPTPCmd(positionCnx00, E_ptpMode.JUMP_XYZ))
    positionCnx00.z = solder.ALTITUDE_PCB
    solder.wait_end_queue(solder.protocol.armOrientationBase.queued.setPTPCmd(positionCnx00, E_ptpMode.JUMP_XYZ))
    pass

if __name__ == '__main__':
    # place_cnx_00()
    solder = SolderEcolow(home=True)

    origin_connector = PositionArm(316.8, -315.2, solder.ALTITUDE_PCB)  # @TODO initialiser avec valeur
    #solder.cycle_clean_solder()
    solder.cycle_solder_board(origin_connector,0,0)
    pass