#!/usr/bin/env python3

from os import path, getenv
from core import handler
from core.dto import CriticalResourceUsageEvent
import handlers
import signal
import websockets
import logging
import asyncio
import psutil


class WebSocketClient:
    def __init__(self, uri, key) -> None:
        self.uri = uri
        self.key = key
        self.websocket = None

        logging.basicConfig(
            format='[%(levelname)s] [%(name)s] %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        handlers.load()

    async def _resource_watcher(self, websocket):
        mem_is_send = False
        disk_is_send = False
        while True:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/mnt/workspace")

            if memory.percent > 95:
                if not mem_is_send:
                    self.logger.warning(f'Critical memory usage: {memory.percent}!')
                    await websocket.send(CriticalResourceUsageEvent("memory", memory).to_json())
                    mem_is_send = True
            else:
                mem_is_send = False

            if disk.percent > 95:
                if not disk_is_send:
                    self.logger.warning(f'Critical disk usage: {disk.percent}!')
                    await websocket.send(CriticalResourceUsageEvent("disk", disk).to_json())
                    disk_is_send = True
            else:
                disk_is_send = False

            await asyncio.sleep(5)

    async def listen(self):
        self.logger.info(f"connecting to {self.uri}")
        async with websockets.connect(f'{self.uri}?key={self.key}') as websocket:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(
                signal.SIGTERM,
                loop.create_task,
                websocket.close()
            )
            asyncio.create_task(self._resource_watcher(websocket))

            async for message in websocket:
                try:
                    self.logger.info(f"received: {message}")

                    result = handler.resolve(message)
                    await websocket.send(result)

                    self.logger.info(f"returned: {result}")
                except Exception as e:
                    self.logger.error(e)


if __name__ == "__main__":
    from dotenv import load_dotenv

    dotenv_file = path.join(path.dirname(__file__), "..", ".env")
    load_dotenv(dotenv_file)

    app = WebSocketClient(getenv("RODONESD_WS_URI"), getenv("RODONESD_KEY"))
    asyncio.run(app.listen())
