import logging
import math
import sys
import time
import os

from polestar.detect_circle_contour import measure_position_center_normalized
from polestar.solderPstar import SolderPstar

_logger = logging.getLogger(__name__)
_logger.level = logging.DEBUG
logging.basicConfig(format="%(asctime)s\t:%(message)s")



from M1.M1_protocol.ProtocolFunctionArmOrientationBase import E_ptpMode
from M1.misc.PositionArm import PositionArm


class SolderPstarCorrect(SolderPstar):
    # Les fichiers de sauvegarde de position connecteur sont dans ce repertoire
    PATH_RESOURCE = (
        #        r"C:\Users\EPI\PycharmProjects\baseCommunicationM1Dobot\polestar\resource"
        r"/home/fc/PycharmProjects/m1/polestar/resource"
    )

    def __init__(self, ip_addr="192.168.1.60", home=False,origin_connector:PositionArm=None):
        super().__init__(ip_addr, home)
        self.origin_connector = origin_connector
        self.org_p = self._load_positions()
        pass


    def _correct_by_camera(self, pad_to_detect:PositionArm, enable:bool=False)->PositionArm:
        """
        Positionne la camera au dessus des points et detecte si la position est correcte,
        :param pad_to_detect: Les pads à detecter.
        :param enable: False, pour rendre les points comme originaux
        :return: Les points corriges par la camera.
        """
        LIMIT_NORME = 0.1
        SCALE_CAMERA_XY = 5
        if not enable:
            return pad_to_detect

        # positionner la camera dessus.
        pointModified =pad_to_detect.copy()
        reference_z = pointModified.z
        while True:
            self.wait_end_queue(
            self.protocol.armOrientationBase.queued.setPTPCmd(pointModified, E_ptpMode.MOVJ_XYZ))

            cRxy = measure_position_center_normalized(False)
            if cRxy is None:
                logging.warning("Impossible de trouver le centre")
                time.sleep(.4)
            else:
                # Si proche du centre
                norme = math.sqrt(cRxy[0]*cRxy[0]+cRxy[1]*cRxy[1])
                if norme <= LIMIT_NORME:
                    pointModified.z = reference_z
                    _logger.debug(f"Vecteur de translation: {pointModified-pad_to_detect}")
                    break
                # proceder selon un zoom deifini par la camera au correctif
                pointModified.x += -cRxy[0]*SCALE_CAMERA_XY
                pointModified.y += cRxy[1] * SCALE_CAMERA_XY
        return pointModified



    def _build_others_solder_pins(self, initial_point: PositionArm)->set:
        """

        :param positions:
        :param initial_point:  1 seul point est donné, les 2 autres points sont tires du gerber.
        :return: Les 3 points calculés
        """
        point = initial_point.copy()
        # point.x += x * self.DIST_BETWEEN_PINS_X
        # point.y += y * self.DIST_BETWEEN_PINS_Y
        point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY
        #positions.add(point)
        point1 = point.copy()
        point1.x -=0.4
        point1.y -=9.4
        positions = set()
        positions.add(point1)
        point2 = point.copy()
        point2.x -=40.1
        point2.y +=3
        positions.add(point2)
        return positions





    def cycle_compute_solder_board(self, x0: int = None, y0: int = None, enable=False):
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
                point = self.get_connector(x, y)
                pad_pcbs =self._build_others_solder_pins( point)
                lst_pads = [ point, *pad_pcbs]
                for nber_pad,point in enumerate(lst_pads):
                    if self.is_connector_loaded(x,y,0):
                        positions.update(lst_pads)
                        break
                    else:
                        point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY
                        point = self._correct_by_camera(point, enable)
                        positions.add(point)
                        self._save_position(point,x,y,nber_pad)
        self.org_p = self._load_positions()
        return positions

    def _build_with_camera_pads_board(self,origin_connector:PositionArm):
        positions = set()

        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                # positionner la tete
                point = self.get_connector(x, y)
                point.z = self.ALTITUDE_PCB + self.HEIGHT_PIN_SECURITY
                point_corrected = self._correct_by_camera(point, False)
                positions.add(point_corrected)


    def _save_position(
        self, pt: PositionArm, connector_x: int, connector_y: int,nber_pad:int
    ):
        point = pt.copy()
        point -=self.origin_connector
        point.z=0
        point.r = 0
        point.save(f"{self.PATH_RESOURCE}/pos{connector_x}{connector_y}_{nber_pad}.pt")
        return point

    def manage_position_pcbs(self):
        # Charger toutes les positions en memoire RAM
        setti = set(self.org_p.values())
        self.cycle_solder_board(setti)
        pass

    def _load_positions(self) -> dict:
        org_p = dict()
        for x in range(self.MATRIX_PCBS_PANEL[0]):
            for y in range(self.MATRIX_PCBS_PANEL[1]):
                for nber_pad in range(self.NBER_PAD):
                    try:
                        point = (PositionArm.load(
                            f"{self.PATH_RESOURCE}/pos{x}{y}_{nber_pad}.pt"
                        ))
                        org_p[f"{x}{y}_{nber_pad}"] = point+self.origin_connector
                    except Exception as e:
                        _logger.debug(f"File not found : {self.PATH_RESOURCE}/pos{x}{y}.pt")
        return org_p

    def is_connector_loaded(self, connector_x: int, connector_y: int,nber_pad:int=0) ->bool:
        return self.org_p.get(f"{connector_x}{connector_y}_{nber_pad}") is not None
    def get_connector(self, connector_x: int, connector_y: int,nber_pad:int=0) -> PositionArm:
        try:
            return self.org_p[f"{connector_x}{connector_y}_{nber_pad}"]
        except KeyError:
            return PositionArm(x=connector_x*self.DIST_BETWEEN_PCB_X,y=connector_y*self.DIST_BETWEEN_PCB_Y)+self.origin_connector

def show_home_solder():
    # Verifier la position
    solder.setHome()
    point = solder.pos
    point.z = 14.8
    solder.wait_end_queue(
        solder.protocol.armOrientationBase.queued.setPTPCmd(point, E_ptpMode.JUMP_XYZ)
    )
    solder.setHome()




if __name__ == "__main__":
    origin_connector = PositionArm(
        100.0-0, +50-3, SolderPstarCorrect.ALTITUDE_PCB, -90
    )  # @TODO initialiser avec valeur
    solder = SolderPstarCorrect(home=True,origin_connector=origin_connector)
    #show_home_solder()
    # Pointe approximativement vers pcb connecterur
    solder.cycle_compute_solder_board(enable=True,x0=None,y0=None)

    while True:
        while True:
            #winsound.Beep(440, 300)
            time.sleep(0.5)
            input("go")
            break
        # solder.cycle_clean_solder()
        # solder._cycle_solder_distribute(True)  # Mettre de la soudure sur le fer
        try:
            solder.manage_position_pcbs()
        except Exception as e:
            _logger.error(e)
        solder.setHome()
    pass
