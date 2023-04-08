import time

import simplepyble


class SolderBle:
    service_uuid = '0000181a-7194-11eb-9439-0242ac130002'
    characteristic_uuid = '00000001-0000-1000-8000-00805f9b34fb'

    def __init__(self):
        self.adapter = simplepyble.Adapter.get_adapters()[0]

    def notified(self,data):
        pass
    def scan_and_connect(self):
        self.adapter.scan_for(5000)
        peripherals =filter(lambda peripheral:peripheral.identifier()=="episolder", self.adapter.scan_get_results())
        if peripherals:
            self.peripheral =next(peripherals)
            self.peripheral.connect()
            contents = self.peripheral.notify(self.service_uuid, self.characteristic_uuid,lambda data: self.notified(data))

    def distribute(self,datas):
        content = "100,1000"
        peripheral.write_request(service_uuid, characteristic_uuid, str.encode(content))
        time.sleep(10)
        pass
