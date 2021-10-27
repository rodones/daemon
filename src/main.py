#!/usr/bin/env python3

from os import path, getenv
from core import handler
import handlers
import signal
import websockets
import logging
import asyncio


class WebSocketClient:
    def __init__(self, uri) -> None:
        self.uri = uri
        self.websocket = None

        logging.basicConfig(
            format='[%(levelname)s] [%(name)s] %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(self.__class__.__name__)

        handlers.load()

    async def listen(self):
        self.logger.info(f"connecting to {self.uri}")
        async with websockets.connect(self.uri) as websocket:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(
                signal.SIGTERM,
                loop.create_task,
                websocket.close()
            )

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

    app = WebSocketClient(getenv("RODONESD_WS_URI"))
    asyncio.run(app.listen())
