import logging
import math
import sys
import time
import os

from polestar.detect_circle_contour import measure_position_center_normalized

# path_root = r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\3dconnexion\dll\x64"
# os.environ['PATH'] += path_root

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

    # Les fichiers de sauvegarde de position connecteur sont dans ce repertoire
    PATH_RESOURCE = (
#        r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\polestar\resource"
        r"/home/fc/PycharmProjects/m1/polestar/resource"
    )
    # pointe une fois pour toute sur le PCB
    ALTITUDE_PCB = 21.5
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
    DIST_BETWEEN_PCB_Y = -20
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
    OFFSET_POINT = PositionArm(0, 0)

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

    def correct_by_camera(self,pads_to_detect,enable:bool=False)->set:
        """
        Positionne la camera au dessus des points et detecte si la position est correcte,
        :param pads_to_detect: Les pads à detecter.
        :param enable: False, pour rendre les points comme originaux
        :return: Les points corriges par la camera.
        """
        LIMIT_NORME = 0.05
        SCALE_CAMERA_XY = 5
        if not enable:
            return pads_to_detect
        pads_modified=set()
        for point in pads_to_detect:
            # positionner la camera dessus.
            pointModified =point.copy()
            while True:
                self.wait_end_queue(
                self.protocol.armOrientationBase.queued.setPTPCmd(pointModified, E_ptpMode.MOVJ_XYZ))

                cRxy = measure_position_center_normalized()
                if cRxy is None:
                    logging.warning("Impossible de trouver le centre")
                    time.sleep(.1)
                else:
                    # Si proche du centre
                    norme = math.sqrt(cRxy[0]*cRxy[0]+cRxy[1]*cRxy[1])
                    if norme <= LIMIT_NORME:
                        pads_modified|=pointModified
                        break
                    # proceder selon un zoom deifini par la camera au correctif
                    pointModified.x += cRxy[0]*SCALE_CAMERA_XY
                    pointModified.y += cRxy[1] * SCALE_CAMERA_XY
        return pads_modified



    def cyle_compute_solder_pins(self,positions:set,initial_point: PositionArm)->set:
        """

        :param positions:
        :param initial_point:  1 seul point est donné, les 2 autres points sont tires du gerber.
        :return: Les 3 points calculés
        """
        point = initial_point.copy()
        # point.x += x * self.DIST_BETWEEN_PINS_X
        # point.y += y * self.DIST_BETWEEN_PINS_Y
        point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY
        positions.add(point)
        point1 = point.copy()
        point1.x -=0.4
        point1.y -=9.4
        positions.add(point1)
        point2 = point.copy()
        point2.x -=40.1
        point2.y +=3
        positions.add(point2)
        return positions


    def cycle_solder_pins(self, point: PositionArm):
        self.protocol.ptpBase.queued.setPtpCommonParams(80, 80)
        # se décaler de 1mm en x pour venir en diagonale
        point.x += self.DIAGONAL
        self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.MOVJ_XYZ)
        self.cycle_solder_pin(point)
        pass



    def cycle_solder_board(self, x0: int = None, y0: int = None, disable=False):
        positions = set()
        assert x0 is None or 0 <= x0 < self.MATRIX_PCBS_PANEL[0]
        assert y0 is None or 0 <= y0 < self.MATRIX_PCBS_PANEL[1]

        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                if x0 is not None and x != x0:
                    continue
                if y0 is not None and y != y0:
                    continue
                # positionner la tete
                point = self._origin_connector(x, y)
                point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY
                positions.add(point)
        # positions contient toutes les positions en attente;
        if disable:  # pour debug ou connaitre les points
            return positions
        # recceuilir toutes les positions
        positions_pin=set()
        for position in positions:
            # pour chaque position d'un point PCB, les 2 autres sont déduits
            pad_pcbs =self.cyle_compute_solder_pins(positions_pin, position)
            pad_pcbs_modified = self.correct_by_camera(pad_pcbs,enable=True)
            positions_pin|=pad_pcbs_modified



        current = PositionArm(0,1000,0)


        self.distrib.distribute(45, 1400, timeout_ms=None)

        while positions_pin:
            point = sorted(positions_pin, key=current.distance)[0]
            positions_pin.remove(point)
            self.protocol.ptpBase.queued.setPtpCommonParams(80, 80)
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
            self.distrib.distribute(45, 700, timeout_ms=None)

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

    def _save_position(
        self, origin_connector: PositionArm, connector_x: int, connector_y: int
    ):
        point = origin_connector.copy()
        point.x += connector_x * self.DIST_BETWEEN_PCB_X
        point.y += connector_y * self.DIST_BETWEEN_PCB_Y
        point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY

        self.protocol.hhtBase.queued.setHttTrigOutputEnabled(False)
        self.wait_end_queue(
            self.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
        )
        #winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        time.sleep(3)
        self.protocol.hhtBase.setHttTrigOutputEnabled(True)
        input(f"positionner le needle ({connector_x}{connector_y})")
        pos = self.pos
        pos.save(f"{self.PATH_RESOURCE}/pos{connector_x}{connector_y}.pt")
        self.protocol.hhtBase.setHttTrigOutputEnabled(False)
        return pos

    def manage_position_pcbs(self, origin_connector: PositionArm):
        # positionnement en Premiere et derniere position

        self.org_p = self._load_positions()
        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                if self.org_p.get(f"{x}{y}") is None:
                    self.org_p[f"{x}{y}"] = self._save_position(origin_connector, x, y)
        self.org_p = self._load_positions()
        pass

    def _load_positions(self) -> dict:
        org_p = dict()
        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                try:
                    org_p[f"{x}{y}"] = PositionArm.load(
                        f"{self.PATH_RESOURCE}/pos{x}{y}.pt1"
                    )
                except Exception as e:
                    _logger.debug(f"File not found : {self.PATH_RESOURCE}/pos{x}{y}.pt")
        return org_p

    def _origin_connector(self, connector_x: int, connector_y: int) -> PositionArm:
        return self.org_p[f"{connector_x}{connector_y}"] + self.OFFSET_POINT


def show_home_solder():
    # Verifier la position
    solder.setHome()
    point = solder.pos
    point.z = 14.8
    solder.wait_end_queue(
        solder.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
    )
    solder.setHome()


def patch_position_connector(solder: SolderPstar):
    connector_x = 1
    connector_y = 4
    org_p = solder._load_positions()
    pt = org_p[f"{connector_x}{connector_y}"]
    pt += PositionArm(-1, 0, 0, 0)
    pt.save(f"{solder.PATH_RESOURCE}/pos{connector_x}{connector_y}.pt")


if __name__ == "__main__":
    solder = SolderPstar(home=True)
    # patch_position_connector(solder)
    # show_home_solder()
    # Pointe approximativement vers pcb connecterur
    origin_connector = PositionArm(
        100.0-2, +50-6.7, solder.ALTITUDE_PCB, -90
    )  # @TODO initialiser avec valeur

    solder.manage_position_pcbs(origin_connector)

    while True:
        while True:
            #winsound.Beep(440, 300)
            time.sleep(0.5)
            input("go")
            break
        # solder.cycle_clean_solder()
        # solder._cycle_solder_distribute(True)  # Mettre de la soudure sur le fer
        try:
            solder.cycle_solder_board()
        except Exception as e:
            _logger.error(e)
        solder.setHome()
    pass
