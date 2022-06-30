#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# inDanger? (next to flames, or next to bomb) (bombNear? and flameNear?)
# healthLow?
# numericalAdvantage? Overall number of unit SUCCESS if > and FAILURE if <=
# healthAdvantage? Either comparison sum of all units lives for each agent, either 1v1 check with the closest enemy
# enemyClose? Check if enemy present in a close radius - Neutral check, can be used for attacking or fleeing

from sre_constants import FAILURE
import py_trees


class SimpleCondition(py_trees.behaviour.Behaviour):
    def __init__(self, name, condition_function):
        super(SimpleCondition, self).__init__(name)
        self.condition_function = condition_function

        self.blackboard = self.attach_blackboard_client(
            name="Simple Conditions")
        self.blackboard.register_key(
            "client", access=py_trees.common.Access.READ)
        self.blackboard.register_key(
            "unit_id", access=py_trees.common.Access.READ)

    def setup(self):
        self.logger.debug("  %s [SimpleCondition::setup()]" % self.name)

    def initialise(self):
        self.logger.debug("  %s [SimpleCondition::initialise()]" % self.name)

    def update(self):
        client = self.blackboard.client
        unit_id = self.blackboard.unit_id

        if self.condition_function(client, unit_id):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

    def terminate(self, new_status):
        self.logger.debug("  %s [SimpleCondition::terminate().terminate()][%s->%s]" %
                          (self.name, self.status, new_status))


class HealthLow(SimpleCondition):
    def __init__(self):
        super().__init__("HealthLow", HealthLow.function)

    def function(client, unit_id):
        return client._state["unit_state"][unit_id]['hp'] == 1


class EnemyClose(SimpleCondition):
    def __init__(self):
        super().__init__("EnemyClose", EnemyClose.function)

    def function(client, unit_id):
        return client._is_enemy_close(unit_id)


class InDanger(SimpleCondition):
    def __init__(self):
        super().__init__("InDanger", InDanger.function)

    def function(client, unit_id):
        # client._is_enemy_close(unit_id) ?
        return client._is_danger_close(unit_id)
