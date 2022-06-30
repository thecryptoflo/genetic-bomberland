import asyncio
from typing import Union
from matplotlib.pyplot import connect, tick_params
import websockets
import json
import time

from websockets.client import WebSocketClientProtocol

_move_set = set(("up", "down", "left", "right"))

MAX_CONNECTION_ATTEMPT = 5


class GameState:
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._state = None
        self._tick_callback = None
        self.connection_attempts = 0
        self.exit = False
        #self.joined_to_early = False

    def set_game_tick_callback(self, generate_agent_action_callback):
        self._tick_callback = generate_agent_action_callback

    async def connect(self):
        try:
            self.connection = await websockets.connect(self._connection_string)
            if self.connection.open:
                return self.connection
        except:
            self.connection_attempts += 1
            if(self.connection_attempts > MAX_CONNECTION_ATTEMPT):
                print("Too many attempts, we quit")
                raise Exception(
                    "Too many connection attempts, server may be down")
            print("Initial connection failed, retrying in 1s")
            time.sleep(1)
            return await self.connect()

    async def _send(self, packet):
        #print("Sending packet "+json.dumps(packet))
        await self.connection.send(json.dumps(packet))

    async def send_move(self, move: str, unit_id: str):
        if move in _move_set:
            packet = {"type": "move", "move": move, "unit_id": unit_id}
            await self._send(packet)

    async def send_bomb(self, unit_id: str):
        packet = {"type": "bomb", "unit_id": unit_id}
        await self._send(packet)

    async def send_detonate(self, x, y, unit_id: str):
        packet = {"type": "detonate", "coordinates": [
            x, y], "unit_id": unit_id}
        await self._send(packet)

    async def send_detonate_last(self, unit_id: str):
        bomb = self._get_bomb_to_detonate(unit_id)
        packet = {"type": "detonate", "coordinates": [
            bomb['x'], bomb['y']], "unit_id": unit_id}
        await self._send(packet)

    async def _handle_messages(self, connection: WebSocketClientProtocol):
        # and not self.joined_to_early:
        while not self.exit and (self._state == None or not self._state.get('isFinished')):
            try:
                raw_data = await connection.recv()
                data = json.loads(raw_data)
                await self._on_data(data)
            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

    async def _on_data(self, data):
        data_type = data["type"]

        if data_type == "info":
            # no operation
            pass
        elif data_type == "game_state":
            payload = data["payload"]
            self._on_game_state(payload)
        elif data_type == "tick":
            payload = data["payload"]
            await self._on_game_tick(payload)
        elif data_type == "endgame_state":
            # if(self._state == None):
            #   self.joined_to_early = True
            #    return
            payload = data["payload"]
            winning_agent_id = payload["winning_agent_id"]
            try:
                self._state['isFinished'] = True
                self._state['winning_agent_id'] = winning_agent_id
            except Exception:
                self.exit = True
            #print(f"Game over. Winner: Agent {winning_agent_id}")
        else:
            print(f"unknown packet \"{data_type}\": {data}")

    def _on_game_state(self, game_state):
        self._state = game_state

    async def _on_game_tick(self, game_tick):
        events = game_tick["events"]
        for event in events:
            event_type = event.get("type")
            if event_type == "entity_spawned":
                self._on_entity_spawned(event)
            elif event_type == "entity_expired":
                self._on_entity_expired(event)
            elif event_type == "unit_state":
                payload = event.get("data")
                self._on_unit_state(payload)
            elif event_type == "entity_state":
                x, y = event.get("coordinates")
                updated_entity = event.get("updated_entity")
                self._on_entity_state(x, y, updated_entity)
            elif event_type == "unit":
                unit_action = event.get("data")
                self._on_unit_action(unit_action)
            else:
                print(f"unknown event type {event_type}: {event}")
        if self._tick_callback is not None:
            tick_number = game_tick.get("tick")
            self._state['tick'] = tick_number
            await self._tick_callback(tick_number, self._state)

    def _on_entity_spawned(self, spawn_event):
        spawn_payload = spawn_event["data"]
        self._state["entities"].append(spawn_payload)

    def _on_entity_expired(self, spawn_event):
        expire_payload = spawn_event["data"]

        def filter_entity_fn(entity):
            [x, y] = expire_payload
            entity_x = entity["x"]
            entity_y = entity["y"]
            should_remove = entity_x == x and entity_y == y
            return should_remove == False

        self._state["entities"] = list(filter(
            filter_entity_fn, self._state["entities"]))

    def _on_unit_state(self, unit_state):
        unit_id = unit_state["unit_id"]
        self._state["unit_state"][unit_id] = unit_state

    def _on_entity_state(self, x, y, updated_entity):
        for entity in self._state["entities"]:
            if entity["x"] == x and entity["y"] == y:
                self._state["entities"].remove(entity)
        self._state["entities"].append(updated_entity)

    def _on_unit_action(self, action_packet):
        unit_id = action_packet["unit_id"]
        unit = self._state["unit_state"][unit_id]
        coordinates = unit["coordinates"]
        action_type = action_packet["type"]
        if action_type == "move":
            move = action_packet["move"]
            if move in _move_set:
                new_coordinates = self._get_new_unit_coordinates(
                    coordinates, move)
                self._state["unit_state"][unit_id]["coordinates"] = new_coordinates
        elif action_type == "bomb":
            # no - op since this is redundant info
            pass
        elif action_type == "detonate":
            # no - op since this is redundant info
            pass
        else:
            print(f"Unhandled agent action recieved: {action_type}")

    def _get_new_unit_coordinates(self, coordinates, move_action) -> Union[int, int]:
        [x, y] = coordinates
        if move_action == "up":
            return [x, y+1]
        elif move_action == "down":
            return [x, y-1]
        elif move_action == "right":
            return [x+1, y]
        elif move_action == "left":
            return [x-1, y]

# Basic checks

    def _can_unit_move(self, unit_id, move):
        unit = self._state["unit_state"][unit_id]
        [x, y] = self._get_new_unit_coordinates(unit["coordinates"], move)

        if not self.is_inbounds(x, y):
            return False

        for id, u in self._state["unit_state"].items():
            [u_x, u_y] = u["coordinates"]
            if u_x == x and u_y == y:
                return False

        for entity in self._state["entities"]:
            if entity["x"] == x and entity["y"] == y and entity["type"] in ["b", "m", "w", "o"]:
                return False
        return True

    def is_inbounds(self, x, y):
        max = self._state["world"]
        return (x >= 0 and x < max["width"]) and (y >= 0 and y < max["height"])

    def _can_place_bomb(self, unit_id):
        unit = self._state["unit_state"][unit_id]
        [x, y] = unit["coordinates"]
        if(unit["inventory"]["bombs"] > 0):
            for entity in self._state["entities"]:
                if entity["x"] == x and entity["y"] == y and entity["type"] == "b":
                    return False
            return True
        return False

    def _can_detonate_bomb(self, unit_id):
        bomb = self._get_bomb_to_detonate(unit_id)
        if(bomb != None and bomb["created"] - self._state["tick"] >= 5):
            return True
        return False

    def _get_bomb_to_detonate(self, unit_id) -> Union[int, int] or None:
        entities = self._state["entities"]
        bombs = list(filter(lambda entity: entity["type"] == "b" and entity["unit_id"] ==
                            unit_id, entities))
        bomb = next(iter(bombs or []), None)
        return bomb

    def _is_enemy_close(self, unit_id):
        unit = self._state["unit_state"][unit_id]

        for u in self._state["unit_state"].values():
            if u["agent_id"] != unit["agent_id"]:
                [u_x, u_y] = u["coordinates"]
                for direction in _move_set:
                    [new_x, new_y] = self._get_new_unit_coordinates(
                        unit["coordinates"], direction)
                    if u_x == new_x and u_y == new_y:
                        return True

        return False

    def _can_attack_enemy(self, unit_id):
        return self._can_place_bomb(unit_id) and self._is_enemy_close(unit_id)

    def _are_entities_near(self, types, unit_id=None, coordinates=None):
        # Check the 3*3 square's corners around the unit / position
        if unit_id:
            unit = self._state["unit_state"][unit_id]
            position = unit["coordinates"]
        else:
            position = coordinates

        for entity in self._state["entities"]:
            if entity["type"] in types:
                for i in range(-1, 2, 2):
                    for j in range(-1, 2, 2):
                        if entity["x"] == position[0] + i and entity["y"] == position[1] + j:
                            return True

    def _are_entities_close(self, types, unit_id=None, coordinates=None):
        # return true if at least one entity with on of the type in types is close, one case away vertically or horizontally
        if unit_id:
            unit = self._state["unit_state"][unit_id]
            position = unit["coordinates"]
        else:
            position = coordinates

        for entity in self._state["entities"]:
            if entity["type"] in types:
                for direction in _move_set:
                    [new_x, new_y] = self._get_new_unit_coordinates(
                        position, direction)
                    if entity["x"] == new_x and entity["y"] == new_y:
                        return True

        return False

    def _are_entities_on_position(self, types, unit_id=None, coordinates=None):
        if unit_id:
            unit = self._state["unit_state"][unit_id]
            position = unit["coordinates"]
        else:
            position = coordinates

        for entity in self._state["entities"]:
            if entity["type"] in types and (entity["x"] == position[0] and entity["y"] == position[1]):
                return True

    def _is_danger_near(self, unit_id):
        return self._is_danger_close(unit_id) or self._are_entities_near(["b", "x"], unit_id=unit_id)

    def _is_danger_close(self, unit_id):
        return self._is_danger_on_position(unit_id) or self._are_entities_close(["b", "x"], unit_id=unit_id)

    def _is_danger_on_position(self, unit_id=None, coordinates=None):
        return self._are_entities_on_position(["b", "x"], unit_id, coordinates)

    def _is_position_safe_close(self, position):
        return not self._is_danger_on_position(coordinates=position) and not self._are_entities_close(["b", "x"], coordinates=position)

    def _is_position_safe_near(self, position):
        return self._is_position_safe_close and not self._are_entities_near(["x"], coordinates=position)

    def _get_safe_moves(self, unit_id):
        unit = self._state["unit_state"][unit_id]
        safe_moves = []

        for move in _move_set:
            [x, y] = self._get_new_unit_coordinates(unit["coordinates"], move)
            if self._can_unit_move(unit_id, move) and not self._is_danger_on_position(coordinates=[x, y]):
                safe_moves.append(move)
        return safe_moves

    def _get_safe_close_moves(self, unit_id):
        unit = self._state["unit_state"][unit_id]
        safe_close_moves = []

        for move in _move_set:
            [x, y] = self._get_new_unit_coordinates(unit["coordinates"], move)
            if self._can_unit_move(unit_id, move) and self._is_position_safe_close([x, y]):
                safe_close_moves.append(move)
        return safe_close_moves

    def _get_safe_near_moves(self, unit_id):
        unit = self._state["unit_state"][unit_id]
        safe_near_moves = []

        for move in _move_set:
            [x, y] = self._get_new_unit_coordinates(unit["coordinates"], move)
            if self._can_unit_move(unit_id, move) and self._is_position_safe_near([x, y]):
                safe_near_moves.append(move)
        return safe_near_moves
