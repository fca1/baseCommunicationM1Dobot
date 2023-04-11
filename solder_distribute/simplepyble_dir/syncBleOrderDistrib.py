import threading
import time
from threading import Lock

import simplepyble


class BleOrderDistrib:
    service_uuid = '0000181a-7194-11eb-9439-0242ac130002'
    characteristic_uuid = '00000001-0000-1000-8000-00805f9b34fb'

    def __init__(self):
        self.adapter = simplepyble.Adapter.get_adapters()[0]
        self.peripheral = None
        self.adapter.set_callback_on_disconnected(lambda peripheral: self.peripheral.connect())
        self.event = threading.Event()
        self.ok = False


    def _notified(self, data):
        self.ok = b"ok" in data
        self.event.set()
        pass
    def scan_and_connect(self):
        self.adapter.scan_for(5000)
        peripherals =filter(lambda peripheral:peripheral.identifier()=="episolder", self.adapter.scan_get_results())
        if peripherals:
            self.peripheral =next(peripherals)
            self.peripheral.connect()
            self.peripheral.notify(self.service_uuid, self.characteristic_uuid, lambda data: self._notified(data))

    def distribute(self,*datas,timeout_ms:int=None) -> bool:
        """
        valeurs par binome, comprenant la vitesse de -100% a 100% et le temps. Par exemple, 100,200,-100,50 va apporter de la soudure pendant 200ms et la retracter pendant 50ms
        :param datas:
        :return:
        """

        content = ",".join([str(x) for x in datas])
        self.ok = True
        if timeout_ms:
            self.event.clear()
        self.peripheral.write_request(self.service_uuid, self.characteristic_uuid, str.encode(content))
        if timeout_ms:
            if not self.event.wait(timeout=timeout_ms/1000):
                return False
        return self.ok
