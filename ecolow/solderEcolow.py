import logging
import sys
import time

import winsound

from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm
from jog3dconnexion import JogM1
from m1 import M1
from solder_distribute.simplepyble_dir.syncBleOrderDistrib import BleOrderDistrib


class SolderEcolow(M1):
    """
    Le robot est faux sur x,y impossible de calibrer quoi que ce soit.
    La nouvelle méthode consiste à:
    * pointer avec le needle, les 4 points montrants les connecteurs en 0,0 0,4 1,0 et 1,4
    * utiliser cela pour souder en travaillant ensuite avec le robot x,y (deplacement faible = erreur faible)

    """
    # Les fichiers de sauvegarde de position connecteur sont dans ce repertoire
    PATH_RESOURCE=r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\ecolow\resource"
    # pointe une fois pour toute
    ALTITUDE_PCB=56.2
    # en mm
    # Les signes negatifs sont pour le deplacement (selon x+ et y+)
    # Dans le cas présent, la longueur la plus grande du PCB est Y.
    # Description du PCB
    # Dimension du panel complet 
    DIM_PANELX=156
    DIM_PANELY=240
    #
    MATRIX_PCBS_PANEL=(2, 5)
    DIST_BETWEEN_PCB_X =72
    DIST_BETWEEN_PCB_Y=-45.65
    # description du connexteur
    MATRIX_INSIDE_CONNECTOR=(3,2)
    DIST_BETWEEN_PINS_X=4.56
    DIST_BETWEEN_PINS_Y =-9.12
    HEIGHT_PIN_SECURITY=5   # hauteur relative par rapport au PCB
    
    OUTPUT_CMD_DISTRIBUTE=18 # Commande pour demander soudure au distributeur (mode pas ble)
    INPUT_CMD_DISTRIBUTE=20  # Attente triggger suite ordre par BLE ou commande relay

    # Une grille est au dessus du PCB avec une epaisseur de 10mm, cette variable permet de passer cette grille
    HEIGHT_SHAPE = 10

    # En passant par la fonction JUMP, il est possible de pouvoir choisir 2 planchers.
    # Plancher interdisant de varier (X,Y)
    DEFECTOR_LENGTH = 45
    #  Lors de la descente sur la pin, fait varier selon une pente (HEIGHT_PIN_SECURITY/DIAGONAL)
    DIAGONAL=-2
    # Le needle est sur le centre pin connecteur, cet offset permet le decalage
    OFFSET_POINT=PositionArm(+1.5,0)

    def __init__(self,ip_addr="192.168.0.55",home=False):
        # Communication avec le dobot M1
        super().__init__(ip_addr=ip_addr)
        self.distrib = BleOrderDistrib()
        self.org_p = dict()

        # Le pot de nettoyage du fer a souder 
        self.clean_solder = PositionArm(100,0,70)   #


        self.initialize()
        if home:
            self.setHome()

        # Gestion des hauteurs de securité
        self._configure_jumpJ()
        pass

    def initialize(self):
        try:
            self.initialize_origin()
            self._init_io()
            self.initialize_arm()           # Choix gauche ou droit
            self.initialize_length_defector(self.DEFECTOR_LENGTH)

            # La connextion BLE est faite une fois pour toute.
            if not self.distrib.scan_and_connect():
                raise Exception("Impossible de se connecter au distributeur soudure")
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
        self.protocol.ptpBase.setPtpJumpParams(self.HEIGHT_SHAPE,self.ALTITUDE_PCB+self.HEIGHT_SHAPE)
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
            # se décaler de 1mm en x pour venir en diagonale
            point.x+=self.DIAGONAL
            self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
            self.cycle_solder_pin(point)
            pass
        pass


    def cycle_solder_board(self,x0:int=None,y0:int=None,disable=False)  :
        positions = set()
        assert x0 is None or 0<=x0<self.MATRIX_PCBS_PANEL[0]
        assert y0 is None or 0 <= y0 < self.MATRIX_PCBS_PANEL[1]

        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                if x0 is not None and x!= x0:
                    continue
                if y0 is not None and y!= y0:
                    continue
                # positionner la tete
                point = self._origin_connector(x, y)
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


    def _cycle_solder_distribute(self, wett:bool=False) -> None:
        # La distribution se fait via ble
        # self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,1)
        # self.protocol.waitBase.queued.setWaitms(300 if is_short else is_short)
        # self.wait_end_queue(self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,0))
        if not wett:
            time.sleep(2)
            if not self.distrib.distribute(30,1800,timeout_ms=0):
                logging.error("Probleme de distribution de soudure")
            time.sleep(3)
        else:
            if not self.distrib.distribute(30,1250,timeout_ms=0):
                logging.error("Probleme de distribution de soudure")






    def cycle_solder_pin(self,initial_point:PositionArm) -> None:
        """
        Le pointe a souder est en hauteur à 1mm en Y
        :return:
        """


        self.protocol.ptpBase.queued.setPtpCommonParams(1, 5)
        point = initial_point.copy()
        # Retirer  x  1mm (pour amener la panne en diagonale)
        point.x-=self.DIAGONAL
        point.z = self.ALTITUDE_PCB
        #time.sleep(2)
        # Mettre en position soudage
        try:
            self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ))
            self._cycle_solder_distribute() # Mettre de la soudure sur le fer
        finally:
            self.protocol.ptpBase.queued.setPtpCommonParams(10, 10)
            point = initial_point.copy()
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
        self.setHome()
        pass




    def start_cycle(self):
        pass

    def _save_position(self, origin_connector:PositionArm, connector_x:int, connector_y:int):
        point = origin_connector.copy()
        point.x += connector_x * self.DIST_BETWEEN_PCB_X
        point.y += connector_y * self.DIST_BETWEEN_PCB_Y
        point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY

        self.protocol.hhtBase.queued.setHttTrigOutputEnabled(False)
        self.wait_end_queue(self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ))
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        time.sleep(3)
        self.protocol.hhtBase.setHttTrigOutputEnabled(True)
        input(f"positionner le needle ({connector_x}{connector_y})")
        pos = self.pos
        pos.save(f"{self.PATH_RESOURCE}/pos{connector_x}{connector_y}.pt")
        self.protocol.hhtBase.setHttTrigOutputEnabled(False)
        return pos

    def manage_position_pcbs(self,origin_connector: PositionArm):
        # positionnement en Premiere et derniere position

        self.org_p = self._load_positions()
        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                if  self.org_p.get(f"{x}{y}") is None:
                    self.org_p[f"{x}{y}"] = self._save_position(origin_connector, x, y)
        self.org_p = self._load_positions()
        pass

    def _load_positions(self) ->dict:
        org_p=dict()
        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                try:
                    org_p[f"{x}{y}"]=PositionArm.load(f"{self.PATH_RESOURCE}/pos{x}{y}.pt")
                except Exception as e:
                    logging.debug(f"File not found : {self.PATH_RESOURCE}/pos{x}{y}.pt")
        return org_p

    def _origin_connector(self, connector_x:int, connector_y:int) ->PositionArm:
        return self.org_p[f"{connector_x}{connector_y}"]+self.OFFSET_POINT

def show_home_solder():
    # Verifier la position
    solder.setHome()
    point = solder.pos
    point.z = 21
    solder.wait_end_queue(solder.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ))
    solder.setHome()

def patch_position_connector(solder:SolderEcolow):
    connector_x=1
    connector_y=4
    org_p = solder._load_positions()
    pt = org_p[f"{connector_x}{connector_y}"]
    pt += PositionArm(-1,0,0,0)
    pt.save(f"{solder.PATH_RESOURCE}/pos{connector_x}{connector_y}.pt")

if __name__ == '__main__':
    solder = SolderEcolow(home=True)
    #patch_position_connector(solder)
    #show_home_solder()
    # Pointe approximativement vers pcb connecterur
    origin_connector = PositionArm(128.62, -118.38, solder.ALTITUDE_PCB,-90)  # @TODO initialiser avec valeur

    solder.manage_position_pcbs(origin_connector)

    while True:
        # Attente touche left
        with JogM1(solder) as jog:
            while True:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                time.sleep(1)
                bleft, bright = jog.read()
                if bleft:
                    break
        solder.cycle_clean_solder()
        solder._cycle_solder_distribute(True)  # Mettre de la soudure sur le fer
        solder.cycle_solder_board()
        solder.setHome()
    solder.cycle_solder_board(1,2)
    solder.cycle_solder_board(1,1)
    solder.cycle_solder_board(1,0)
    solder.cycle_solder_board(1,4)
    pass