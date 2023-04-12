import threading
import time
from threading import Lock

import simplepyble


class BleOrderDistrib:
    service_uuid = '0000181a-7194-11eb-9439-0242ac130002'
    characteristic_uuid = '00000001-0000-1000-8000-00805f9b34fb'

    def __init__(self,bias:int=0):
        self.adapter = simplepyble.Adapter.get_adapters()[0]
        self.peripheral = None
        self.event = threading.Event()
        self.ok = False
        self.bias = bias
        self._forward = False

    def setBias(self,value_ms:int):
        self.bias = value_ms


    def _notified(self, data):
        self.ok = b"ok" in data
        self.event.set()
        pass
    def scan_and_connect(self):
        self.adapter.scan_for(5000)
        peripherals =filter(lambda peripheral:peripheral.identifier()=="episolder", self.adapter.scan_get_results())
        if peripherals:
            self.peripheral =next(peripherals)
            self.peripheral.set_callback_on_disconnected(lambda peripheral: self.peripheral.connect())
            self.peripheral.connect()
            self.peripheral.notify(self.service_uuid, self.characteristic_uuid, lambda data: self._notified(data))

    def distribute(self,*datas,timeout_ms:int=None) -> bool:
        """
        valeurs par binome, comprenant la vitesse de -100% a 100% et le temps. Par exemple, 100,200,-100,50 va apporter de la soudure pendant 200ms et la retracter pendant 50ms
        :param datas:
        :return:
        """
        assert (len(datas)//2)*2 == len(datas)
        # en cas de changement de sens, introduit la notion d'hysteresis
        cpl = [int(x) for x in datas]
        trs = []
        tmo_ms = 1000
        while cpl:
            pcent,time_ms =cpl.pop(0),cpl.pop(0)
            if pcent>=0 and not self._forward:
                time_ms+=self.bias
                self._forward = True
            if pcent<0 and self._forward:
                time_ms+=self.bias
                self._forward = False
            trs.append(pcent)
            trs.append(time_ms)
            tmo_ms+=time_ms



        content = ",".join([str(x) for x in trs])

        self.ok = True
        if timeout_ms:
            self.event.clear()
        self.peripheral.write_request(self.service_uuid, self.characteristic_uuid, str.encode(content))
        if timeout_ms is not None:
            # Si timeout_ms=0 c'est une gestion automatique du timeout qui est mise en place
            if not self.event.wait(timeout=timeout_ms/1000 if timeout_ms else tmo_ms/1000):
                return False
        return self.ok

if __name__ == '__main__':
    distrib = BleOrderDistrib(400)
    distrib.scan_and_connect()
    distrib.distribute(-100,1000,-100,100,100,200,timeout_ms=2000)
    pass
