#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import py_trees
import asyncio


class SimpleAction(py_trees.behaviour.Behaviour):
    def __init__(self, name, action):
        super(SimpleAction, self).__init__(name)
        self.action = action
        self.blackboard = self.attach_blackboard_client(name="SimpleAction")
        self.blackboard.register_key(
            "client", access=py_trees.common.Access.READ)
        self.blackboard.register_key(
            "unit_id", access=py_trees.common.Access.READ)

    def setup(self):
        self.logger.debug("  %s [SimpleAction::setup()]" % self.name)

    def initialise(self):

        self.logger.debug("  %s [SimpleAction::initialise()]" % self.name)

    def update(self):
        self.logger.debug("  %s [Foo::update()]" % self.name)
        loop = asyncio.get_running_loop()
        client = self.blackboard.client
        unit_id = self.blackboard.unit_id

        if self.action == "idle":
            return py_trees.common.Status.SUCCESS
        elif self.action == "bomb" and client._can_place_bomb(unit_id):
            asyncio.run_coroutine_threadsafe(client.send_bomb(unit_id), loop)
            return py_trees.common.Status.SUCCESS

        elif self.action == "detonate" and client._can_detonate_bomb(unit_id):
            asyncio.run_coroutine_threadsafe(
                client.send_detonate_last(unit_id), loop)
            return py_trees.common.Status.SUCCESS

        elif self.action in ["up", "down", "left", "right"] and client._can_unit_move(unit_id, self.action):
            asyncio.run_coroutine_threadsafe(
                client.send_move(self.action, unit_id), loop)
            return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE

    def terminate(self, new_status):
        """
        When is this called?
           Whenever your behaviour switches to a non-running state.
            - SUCCESS || FAILURE : your behaviour's work cycle has finished
            - INVALID : a higher priority branch has interrupted, or shutting down
        """
        self.logger.debug("  %s [Foo::terminate().terminate()][%s->%s]" %
                          (self.name, self.status, new_status))


class PlaceBomb(SimpleAction):
    def __init__(self):
        super().__init__("PlaceBomb", "bomb")


class DetonateLastBomb(SimpleAction):
    def __init__(self):
        super().__init__("DetonateLastBomb", "detonate")


class MoveUp(SimpleAction):
    def __init__(self):
        super().__init__("MoveUp", "up")


class MoveDown(SimpleAction):
    def __init__(self):
        super().__init__("MoveDown", "down")


class MoveLeft(SimpleAction):
    def __init__(self):
        super().__init__("MoveLeft", "left")


class MoveRight(SimpleAction):
    def __init__(self):
        super().__init__("MoveRight", "right")


class Idle(SimpleAction):
    def __init__(self):
        super().__init__("Idle", "idle")
