#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import randrange
import py_trees
import asyncio

# moveToSafe (=flee from bomb or flames) // Can be SUCCESS if not threatened in new coords, RUNNING if not totally safe or FAILURE if the current coords is safer than the new position
# goToNearestPowerUp () Can be SUCCESS (if we actually capture the PU), RUNNING, FAILURE (if there's no powerups)
# goToEnemy () ?  Attacking move, maybe good strat if in numerical superiority
# goToSomething functions could use A* algo
# moveToCenter () ?

# AttackEnemy : If enemy on case close to line
# FleeFromDanger
# MoveToward "center" or powerup for example


class ComplexAction(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client(name="Complex Actions")
        self.blackboard.register_key(
            "client", access=py_trees.common.Access.READ)
        self.blackboard.register_key(
            "unit_id", access=py_trees.common.Access.READ)

    def setup(self):
        self.logger.debug("  %s [ComplexAction::setup()]" % self.name)

    def initialise(self):

        self.logger.debug("  %s [ComplexAction::initialise()]" % self.name)

    def update(self):
        self.logger.debug("  %s [ComplexAction::update()]" % self.name)

        return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        self.logger.debug("  %s [ComplexAction::terminate().terminate()][%s->%s]" %
                          (self.name, self.status, new_status))


class AttackEnemy(ComplexAction):
    def __init__(self):
        super().__init__("AttackEnemy")

    def update(self):
        loop = asyncio.get_running_loop()
        client = self.blackboard.client
        unit_id = self.blackboard.unit_id

        if client._can_attack_enemy(unit_id):
            asyncio.run_coroutine_threadsafe(client.send_bomb(unit_id), loop)
            py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE


class MoveToSafePlace(ComplexAction):
    def __init__(self):
        super().__init__("MoveToSafePlace")

    def update(self):
        loop = asyncio.get_running_loop()
        client = self.blackboard.client
        unit_id = self.blackboard.unit_id

        if client._is_danger_near(unit_id):

            if client._is_danger_on_position(unit_id):
                safe_moves = client._get_safe_moves(unit_id)
                if safe_moves:
                    move = safe_moves[randrange(len(safe_moves))]
                    asyncio.run_coroutine_threadsafe(
                        client.send_move(move, unit_id), loop)
                    return py_trees.common.Status.SUCCESS

            elif client._is_danger_close(unit_id):
                safe_close_moves = client._get_safe_close_moves(unit_id)
                safe_near_moves = client._get_safe_near_moves(unit_id)

                if safe_near_moves:
                    move = safe_near_moves[randrange(len(safe_near_moves))]
                    asyncio.run_coroutine_threadsafe(
                        client.send_move(move, unit_id), loop)
                    return py_trees.common.Status.SUCCESS

                elif safe_close_moves:
                    move = safe_close_moves[randrange(len(safe_close_moves))]
                    asyncio.run_coroutine_threadsafe(
                        client.send_move(move, unit_id), loop)
                    return py_trees.common.Status.SUCCESS
            else:
                safe_near_moves = client._get_safe_near_moves(unit_id)
                if safe_near_moves:
                    move = safe_near_moves[randrange(len(safe_near_moves))]
                    asyncio.run_coroutine_threadsafe(
                        client.send_move(move, unit_id), loop)
                    return py_trees.common.Status.SUCCESS

            return py_trees.common.Status.FAILURE

        return py_trees.common.Status.SUCCESS
