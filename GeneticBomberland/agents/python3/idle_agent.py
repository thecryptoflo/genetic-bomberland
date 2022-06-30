from typing import Union
from game_state import GameState
import asyncio
import random
import os

actions = ["up", "down", "left", "right", "bomb", "detonate"]


class IdleAgent():
    name = "IdleAgent"

    def __init__(self, agentId):
        uri = os.environ.get('GAME_CONNECTION_STRING')
        if(uri is None):
            uri = f"ws://127.0.0.1:3000/?role=agent&agentId={agentId}&name={IdleAgent.name}"
        self._client = GameState(uri)

        # any initialization code can go here
        self._client.set_game_tick_callback(self._on_game_tick)

        try:
            loop = asyncio.get_event_loop()
            connection = loop.run_until_complete(self._client.connect())
            print("Connection successfull")
            tasks = [
                asyncio.ensure_future(
                    self._client._handle_messages(connection)),
            ]
            loop.run_until_complete(asyncio.wait(tasks))
        except Exception:
            print("Can't connect, server may be down")

    async def _on_game_tick(self, tick_number, game_state):
        # do Nothing here, we're idleing here
        # Maybe also try to setup a Wandering agent ?
        return
