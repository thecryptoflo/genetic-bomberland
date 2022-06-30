import asyncio
from matplotlib.pyplot import connect
import websockets
from websockets.client import WebSocketClientProtocol
import json


class Admin():
    def __init__(self):
        self.uri = "ws://127.0.0.1:3000/?role=admin"

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())

    async def connect(self):
        self.connection = await websockets.connect(self.uri)
        if self.connection.open:
            return self.connection

    async def _send(self, packet):
        await self.connection.send(json.dumps(packet))

    async def send_reset(self):
        packet = {"type": "request_game_reset"}
        await self._send(packet)

    def reset_server(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.send_reset())
        except websockets.exceptions.ConnectionClosed:
            print('Connection closed : Reconnecting')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.connect())
            self.reset_server()

    async def close_connection(self):
        await self.connection.close()

    def disconnect(self):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.close_connection())
        except websockets.exceptions.ConnectionClosed:
            print('Connection with server closed')
