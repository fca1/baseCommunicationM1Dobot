import logging
import threading
import time
from threading import Lock

import simplepyble

_logger = logging.getLogger(__name__)
_logger.level = logging.DEBUG
logging.basicConfig(format="%(asctime)s\t:%(message)s")


class BleOrderDistrib:
    service_uuid = "0000181a-7194-11eb-9439-0242ac130002"
    characteristic_uuid = "00000001-0000-1000-8000-00805f9b34fb"

    def __init__(self, bias: int = 0):
        self.adapter = simplepyble.Adapter.get_adapters()[0]
        self._lock = threading.Lock()
        self.peripheral = None
        self.event = threading.Event()
        self.event.set()
        self.ok = False
        self.bias = bias
        self._forward = False

    def setBias(self, value_ms: int):
        self.bias = value_ms

    def _notified(self, data):
        self.ok = b"ok" in data
        self.event.set()
        pass

    def _connect(self,enabled=True):
        if enabled:
            try:
                _logger.info(f"candidate: {self.peripheral.rssi()}dBm")
                self.peripheral.connect()
                _logger.debug(f"connected {self.peripheral.rssi()}dBm")
                self.peripheral.notify(
                    self.service_uuid,
                    self.characteristic_uuid,
                    lambda data: self._notified(data),
                )
            except RuntimeError as e:
                _logger.warning("impossible de se connecter BLE")
                return False
            _logger.debug(f"Ble is ready")
        else:
            self.peripheral.disconnect()
    def scan_and_connect(self) -> bool:
        if self.peripheral:
            if self.peripheral.is_connected():
                return True
            _logger.debug("attempt to rescan")
            self.peripheral = None
        with self._lock:
            while True:
                self.adapter.scan_for(5000)
                _logger.debug("attempt to connect")
                peripherals = tuple(
                    filter(
                        lambda peripheral: peripheral.identifier() == "episolder",
                        self.adapter.scan_get_results(),
                    )
                )
                if peripherals:
                    break
            self.peripheral = peripherals[0]
            return True

    def wait_end_distribute(self, timeout_ms: int = 0) -> bool:
        # Si timeout_ms=0 c'est une gestion automatique du timeout qui est mise en place
        return self.event.wait(timeout=timeout_ms / 1000)

    def distribute(self, *datas, timeout_ms: int = None) -> bool:
        """
        valeurs par binome, comprenant la vitesse de -100% a 100% et le temps. Par exemple, 100,200,-100,50 va apporter de la soudure pendant 200ms et la retracter pendant 50ms
        :param datas:
        :return:
        """
        assert (len(datas) // 2) * 2 == len(datas)
        if not self.scan_and_connect():
            _logger.warning(f"Ordre ble non execute: {datas}")
            return False
        # en cas de changement de sens, introduit la notion d'hysteresis
        cpl = [int(x) for x in datas]
        trs = []
        tmo_ms = 1000
        while cpl:
            pcent, time_ms = cpl.pop(0), cpl.pop(0)
            if pcent >= 0 and not self._forward:
                time_ms += self.bias
                self._forward = True
            if pcent < 0 and self._forward:
                time_ms += self.bias
                self._forward = False
            trs.append(pcent)
            trs.append(time_ms)
            tmo_ms += time_ms

        content = ",".join([str(x) for x in trs])

        self.ok = True
        with self._lock:
            self.event.clear()
            try:
                self.peripheral.write_request(
                    self.service_uuid, self.characteristic_uuid, str.encode(content)
                )
            except RuntimeError as e:
                _logger.warning(f"Ordre ble non execute: {datas}")
                return False
            if timeout_ms is not None:
                # Si timeout_ms=0 c'est une gestion automatique du timeout qui est mise en place
                if not self.event.wait(
                    timeout=timeout_ms / 1000 if timeout_ms else tmo_ms / 1000
                ):
                    return False
            return self.ok


if __name__ == "__main__":
    distrib = BleOrderDistrib(400)
    distrib.scan_and_connect()
    distrib.distribute(-100, 1000, -100, 100, 100, 200, timeout_ms=20000)
    pass
