from typing import Union
from game_state import GameState
import asyncio
import random
import os
import py_trees  # https://py-trees.readthedocs.io/en/devel/modules.html?highlight=swap#py_trees.trees.BehaviourTree
from BTree import BTree

actions = ["up", "down", "left", "right", "bomb", "detonate"]


class GenAgent():
    name = "GenAgent"

    def __init__(self, btree_json, agentId, return_list=None):
        uri = os.environ.get('GAME_CONNECTION_STRING')
        if uri == None:
            uri = f"ws://127.0.0.1:3000/?role=agent&agentId={agentId}&name={GenAgent.name}"
        self._client = GameState(uri)
        self.blackboard = py_trees.blackboard.Client(name="Tree Config")
        self.blackboard.register_key(
            "client", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(
            "unit_id", access=py_trees.common.Access.WRITE)
        self.blackboard.client = self._client
        self.blackboard.unit_id = None

        # any initialization code can go here
        self.btree = BTree.tree_from_json(btree_json)
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

            # if(self._client.joined_to_early):
            #    return

            if return_list != None:
                return_list.append(self._client._state)

        except Exception:
            print("Can't connect, server may be down")

    # returns coordinates of the first bomb placed by a unit
    def _get_bomb_to_detonate(self, unit) -> Union[int, int] or None:
        entities = self._client._state.get("entities")
        bombs = list(filter(lambda entity: entity.get(
            "unit_id") == unit and entity.get("type") == "b", entities))
        bomb = next(iter(bombs or []), None)
        if bomb != None:
            return [bomb.get("x"), bomb.get("y")]
        else:
            return None

    async def _on_game_tick(self, tick_number, game_state):

        # get my units
        my_agent_id = game_state.get("connection").get("agent_id")
        my_units = game_state.get("agents").get(my_agent_id).get("unit_ids")

        # send each unit a random action
        for unit_id in my_units:
            if(self._client._state["unit_state"][unit_id]['hp'] > 0):
                self.blackboard.unit_id = unit_id
                self.btree.tick()
