import asyncio
import logging

from bleak import BleakError, BleakScanner

from solder_distribute.bleclientsolder import BleClientSolder

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG   # FCA007
logging.basicConfig(format='%(asctime)s\t:%(message)s')



async def main():
    logging.basicConfig(level=logging.INFO)

    # bles = filter(lambda ble: ble.name=="episolder", await BleakScanner.discover(timeout=5))
    ble= await BleakScanner.find_device_by_name("episolder")
    # 'F4:12:FA:DC:B6:EE'
    if 1:
        while True:
            try:
                async with  BleClientSolder(ble) as solder:
                    result = await solder.wait_solder(1,50,timeout=4)
            except BleakError:
                print("ca sent la deconnection")
                break
            except Exception as e:
                print(e)
                break
    pass


asyncio.run(main())
