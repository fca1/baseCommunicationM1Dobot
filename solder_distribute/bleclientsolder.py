import asyncio
import logging
import re
import copy

from bleak import BLEDevice, AdvertisementData, BleakClient

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG   # FCA007
logging.basicConfig(format='%(asctime)s\t:%(message)s')



class BleClientSolder(BleakClient):
    _solderUUID = '00000001-0000-1000-8000-00805f9b34fb'
    def __init__(self, client : [BleakClient,BLEDevice],advertising_data: [None,AdvertisementData] = None  ):
        super().__init__(client,advertising_data)
        pass


    async def ask_is_ready(self) -> bool:
        data = bytes(await self.read_gatt_char(self._solderUUID))
        return  data.decode()=="ok"
        return int(r)

    async def set_solder_pcent(self, pcent:int=0,time_ms:int=0):
        assert -100<=pcent<=100
        await self.write_gatt_char(self._solderUUID,f"{pcent},{time_ms}".encode(), response=True)



    async def wait_solder(self, pcent:int=0,time_ms:int=0, timeout=8):
        self.ans=None
        evt = asyncio.Event()
        assert -100<=pcent<=100

        def notification_handler(_, data):
            logger.debug(f"notification {data}")
            self.ans = data.decode()
            evt.set()


        try:
            await self.start_notify(self._solderUUID, notification_handler)
            await self.write_gatt_char(self._solderUUID, f"{int(pcent)},{int(time_ms)}".encode(), response=False)
            await asyncio.wait_for(evt.wait(), timeout)
        except asyncio.exceptions.TimeoutError as e:
            logger.debug("pas de reponse")
        finally:
            await self.stop_notify(self._solderUUID)
        return self.ans=="ok"

