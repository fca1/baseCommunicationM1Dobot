import asyncio
import logging

from bleak import BleakError, BleakScanner

from solder_distribute.bleclientsolder import BleClientSolder

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG   # FCA007
logging.basicConfig(format='%(asctime)s\t:%(message)s')


class SolderBle:
    def __init__(self):
        self.ble = None
        pass
    async def find_ble(self):
        self.ble = await BleakScanner.find_device_by_name("episolder",timeout=15)



async def main():
    logging.basicConfig(level=logging.INFO)

    # bles = filter(lambda ble: ble.name=="episolder", await BleakScanner.discover(timeout=5))
    ble= await BleakScanner.find_device_by_name("episolder")
    # 'F4:12:FA:DC:B6:EE'
    if ble:
        while True:
            try:
                async with  BleClientSolder(ble) as solder:
                    result = await solder.wait_solder((100,5000,-100,5000),timeout=10)
                    print(result)
            except BleakError:
                print("ca sent la deconnection")
                break
            except asyncio.CancelledError as e:
                print(e)
                continue
            except Exception as e:
                print(e)
                break
    pass


asyncio.run(main())
