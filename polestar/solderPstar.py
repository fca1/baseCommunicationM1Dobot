import logging
import math
import sys
import time
import os

from polestar.detect_circle_contour import measure_position_center_normalized


_logger = logging.getLogger(__name__)
_logger.level = logging.DEBUG
logging.basicConfig(format="%(asctime)s\t:%(message)s")



from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm
from m1 import M1
from solder_distribute.simplepyble_dir.syncBleOrderDistrib import BleOrderDistrib


class SolderPstar(M1):
    """
    Le robot est faux sur x,y impossible de calibrer quoi que ce soit.
    La nouvelle méthode consiste à:
    * pointer avec le needle, les 4 points montrants les connecteurs en 0,0 0,4 1,0 et 1,4
    * utiliser cela pour souder en travaillant ensuite avec le robot x,y (deplacement faible = erreur faible)

    """

    # pointe une fois pour toute sur le PCB
    ALTITUDE_PCB = 17.5
    # en mm
    # Les signes negatifs sont pour le deplacement (selon x+ et y+)
    # Dans le cas présent, la longueur la plus grande du PCB est Y.
    # Description du PCB
    # Dimension du panel complet
    DIM_PANELX = 156
    DIM_PANELY = 240
    #
    MATRIX_PCBS_PANEL = (3, 15)
    DIST_BETWEEN_PCB_X = 55
    DIST_BETWEEN_PCB_Y = -20.5
    # description du connexteur
    HEIGHT_PIN_SECURITY = 4  # hauteur relative par rapport au PCB

    OUTPUT_CMD_DISTRIBUTE = (
        18  # Commande pour demander soudure au distributeur (mode pas ble)
    )
    INPUT_CMD_DISTRIBUTE = 20  # Attente triggger suite ordre par BLE ou commande relay

    # Une grille est au dessus du PCB avec une epaisseur de 10mm, cette variable permet de passer cette grille
    HEIGHT_SHAPE = 5

    # En passant par la fonction JUMP, il est possible de pouvoir choisir 2 planchers.
    # Plancher interdisant de varier (X,Y)
    DEFECTOR_LENGTH = 45
    #  Lors de la descente sur la pin, fait varier selon une pente (HEIGHT_PIN_SECURITY/DIAGONAL)
    DIAGONAL = 0
    # Le needle est sur le centre pin connecteur, cet offset permet le decalage sur la pin1 de chaque connecteur
    OFFSET_POINT = PositionArm(x=-2.5,y=-1)

    # Nbre de points (pad) par carte
    NBER_PAD = 3

    def __init__(self, ip_addr="192.168.1.60", home=False):
        # Communication avec le dobot M1
        super().__init__(ip_addr=ip_addr)
        self.distrib = BleOrderDistrib()
        self.org_p = dict()

        # Le pot de nettoyage du fer a souder
        self.clean_solder = PositionArm(100, 0, 70)  #

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
            self.initialize_arm()  # Choix gauche ou droit
            self.initialize_length_defector(self.DEFECTOR_LENGTH)

            # La connextion BLE est faite une fois pour toute.
            if not self.distrib.scan_and_connect():
                raise Exception("Impossible de se connecter au distributeur soudure")
        except Exception as e:
            _logger.error(e)
            sys.exit(1)

    def _init_io(self):
        # stopper distri

        self.protocol.eioBase.setDo(self.OUTPUT_CMD_DISTRIBUTE, 0)
        pass

    def _configure_jumpJ(self):
        # 2 plafonds sont prévus et mesurés. (la hauteur de securite et celle de déplacement)
        # Par rapport à la hauteur du PCB, monter l'outil de la sécurité avant d'avoir le droit de bouger en x,y
        # Le plafond étant à la meme hauteur max, pas de variation en Z pendant le déplacement.
        self.protocol.ptpBase.setPtpJumpParams(
            self.HEIGHT_SHAPE, self.ALTITUDE_PCB + self.HEIGHT_SHAPE
        )
        pass



    def cycle_solder_pins(self, point: PositionArm):
        self.protocol.ptpBase.queued.setPtpCommonParams(80, 80)
        # se décaler de 1mm en x pour venir en diagonale
        point.x += self.DIAGONAL
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
        self.cycle_solder_pin(point)
        pass



    def cycle_solder_board(self, positions_pinRef:set):
        positions_pin=positions_pinRef.copy()



        current = PositionArm(0,1000,0)


        self.distrib.distribute(45, 1400, timeout_ms=None)

        while positions_pin:
            point = sorted(positions_pin, key=current.distance)[0]
            positions_pin.remove(point)
            point+= self.OFFSET_POINT
            self.protocol.ptpBase.queued.setPtpCommonParams(40, 40)
            # En mode jump, l'altitude de déplacement est SHAPE
            self.wait_end_queue(
                self.protocol.armOrientationBase.queued.setPTPCmd(
                    point, E_ptpMode.JUMP_XYZ
                )
            )
            self.cycle_solder_pins(point)
            current = self.pos
        pass

    def cycle_solder_distribute(self, wett: bool = False) -> None:

        # La distribution se fait via ble
        # self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,1)
        # self.protocol.waitBase.queued.setWaitms(300 if is_short else is_short)
        # self.wait_end_queue(self.protocol.eioBase.queued.setDo(self.OUTPUT_CMD_DISTRIBUTE,0))
        if not wett:
            time.sleep(2)
            if not self.distrib.distribute(35, 1000, timeout_ms=0):
                _logger.error("Probleme de distribution de soudure")
            time.sleep(2)
        else:
            if not self.distrib.distribute(30, 1000, timeout_ms=None):
                _logger.error("Probleme de distribution de soudure")

    def cycle_solder_wait_distributed(self, timeout_ms=None) -> bool:
        return self.distrib.wait_end_distribute(timeout_ms)

    def cycle_solder_pin(self, initial_point: PositionArm) -> None:
        """
        Le pointe a souder est en hauteur à 1mm en Y
        :return:
        """

        self.protocol.ptpBase.queued.setPtpCommonParams(80, 80)
        point = initial_point.copy()
        # Retirer  x  1mm (pour amener la panne en diagonale)
        point.x -= self.DIAGONAL
        point.z = self.ALTITUDE_PCB
        #self.cycle_solder_distribute(True)  # Mettre de la soudure sur le fer
        try:
            self.wait_end_queue(
                self.protocol.armOrientationBase.queued.setPTPCmd(
                    point, E_ptpMode.MOVJ_XYZ
                )
            )
        finally:
            self.protocol.ptpBase.queued.setPtpCommonParams(80, 80)
            point = initial_point.copy()
            #self.distrib.distribute(35, 500, timeout_ms=0)
            time.sleep(1)

            self.wait_end_queue(
                self.protocol.armOrientationBase.queued.setPTPCmd(
                    point, E_ptpMode.MOVJ_XYZ
                )
            )
            self.distrib.distribute(45, 800, timeout_ms=None)

        pass

    def cycle_clean_solder(self) -> None:
        # faire un cycle de nettoyage
        point = self.clean_solder.copy()
        point.r = self.pos.r
        low_ = PositionArm(0, -10, -20, 0)
        high_ = -low_
        self.cycle_solder_distribute(True)
        self.protocol.ptpBase.queued.setPtpCommonParams(20, 20)
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
        self.protocol.ptpBase.queued.setPtpCommonParams(10, 10)
        for i in range(3):
            self.protocol.armOrientationBase.queued.setPTPCmd(
                low_, E_ptpMode.MOVJ_XYZ_INC
            )
            self.protocol.armOrientationBase.queued.setPTPCmd(
                high_, E_ptpMode.MOVJ_XYZ_INC
            )
        self.setHome()
        pass

    def buttons_state(self):
        while True:
            s = self.protocol.eioBase.do(18, 1)
            print(s)
            # xx =
            # s = self.protocol.eioBase.di(18)
            # print(bin(s[0]),bin(s[1]))
        return s

    def start_cycle(self):
        pass




