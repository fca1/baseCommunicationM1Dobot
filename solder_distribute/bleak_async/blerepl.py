import asyncio
import re

from bleak import BleakClient


class ReplDoesntRespond(Exception):
    pass


class BleRepl:
    replUUID = "00000010-0000-1000-8000-00805f9b34fb"

    def __init__(self, client: BleakClient):
        self.client = client
        self.evt = asyncio.Event()
        self.pat = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
        self.is_host = None
        self.server = None

    async def ask_repl(self, ssid: str, passw: str, timeout=10):
        self.server = None
        passphrase = ssid + "," + passw

        def notification_handler(sender, data):
            hostIP = data.decode()
            self.is_host = self.pat.match(hostIP)
            if self.is_host:
                self.server = hostIP
                print(f"host:{self.server}")
            self.evt.set()

        try:
            await self.client.start_notify(self.replUUID, notification_handler)
            self.evt.clear()
            await self.client.write_gatt_char(
                self.replUUID, passphrase.encode(), response=True
            )
            await asyncio.wait_for(self.evt.wait(), timeout)
        except asyncio.exceptions.TimeoutError as e:
            print("pas de reponse")
            raise ReplDoesntRespond()
        except Exception as e:
            print(e)
        finally:
            await self.stop_notify(self.replUUID)
        return self.server
