from attr import asdict
from admin import Admin
from BTree import BTree
from gen_agent import GenAgent
from random_agent import RandomAgent
from idle_agent import IdleAgent

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import copy
import shutil
from random import random
from math import exp
import time
from multiprocessing import Manager, Process
from statistics import mean
import subprocess
import uuid
import json


@dataclass
class GpParams:
    pop_size: int = 20
    init_tree_depth: int = 4
    init_max_child_per_node: int = 4
    init_control_node_per: float = 0.1

    fitness_runs: int = 2
    # Base fitness for dumb agent (IdleAgent, RandomAgent)
    base_fitness: int = 500
    min_fitness: int = 10
    max_nodes_before_penalty: int = 50

    elite_selection: bool = False
    elite_per: float = 0.1

    co_rate: float = 0.4  # Try between 0.1 and 0.5

    # Mutation rate : about probs for each node try 1/n in each tree where n = number of nodes

    # Cumulative Probs for composite nodes to swap if selected for mutation
    mut_comp_swap: float = 0.4
    # Cumulative Probs for composite nodes to have a new (leaf) child swap if selected for mutation
    mut_comp_add: float = 0.9
    # Cumulative Probs for composite nodes to be removed if selected for mutation
    mut_comp_remove: float = 1.0
    # Cumulative Probs for composite nodes to swap if selected for mutation
    mut_leaf_swap: float = 0.9
    # Cumulative Probs for composite nodes to swap if selected for mutation
    mut_leaf_remove: float = 1.0

    max_gen: int = 20

    switch_enemy: bool = True
    n_gen_switch_enemy: int = 5


class GP:

    def __init__(self, id=None, params=GpParams()):
        self.id = id if id else uuid.uuid4()
        self.params = params

        # Saving parameters to logs

        file = Path(f'./logs/{self.id}/params.json')
        file.parent.mkdir(exist_ok=True, parents=True)

        file.write_text(json.dumps(asdict(params), indent=4))

    def run(self):
        population = self.initialize_pop()
        offsprings = []

        enemy = IdleAgent
        enemy_btree = None

        gen_count = 0
        while(gen_count < self.params.max_gen):
            print(f"\n---------- Gen {gen_count} ----------\n")

            self.evaluate_pop(population, offsprings, enemy, enemy_btree)

            population = self.select_pop(population, offsprings)
            self.export_gen(population, gen_count)
            gen_count += 1

            if(self.params.switch_enemy and gen_count % self.params.n_gen_switch_enemy == 0):
                # Pop has been previously sorted
                enemy = GenAgent
                enemy_btree = population[0]

            offsprings_c = self.crossover_pop(population)
            offsprings_m = self.mutate_pop(population)
            offsprings = offsprings_c + offsprings_m

        return population[0]

    def initialize_pop(self):
        # Randomly select a root node between SEQUENCE and FALLBACK (SELECTOR)
        # Randomly select a number of child nodes between 2 and 5 and for each one :
        # Choose if it might be a Control (1/3) or Leaf Node (2/3) and then more precisely which node it should be
        print(f"Initialising pop ({self.params.pop_size})")
        p = self.params
        population = []
        for i in range(p.pop_size):
            population.append(BTree.random_btree(
                p.init_tree_depth, p.init_max_child_per_node, p.init_control_node_per))

        return population

    def start_server():
        print("Starting server...")
        return subprocess.Popen(["docker-compose", "up", "--abort-on-container-exit",
                                 "--force-recreate", "--remove-orphans"])

    def evaluate_pop(self, population, offspring, enemy, enemy_btree=None):
        print("Evaluating population")
        for i in range(len(population)):
            self.fitness(population[i], enemy, enemy_btree)
        print("Evaluating offsprings")
        for i in range(len(offspring)):
            self.fitness(offspring[i], enemy, enemy_btree)

    def fitness(self, btree, enemy, enemy_btree=None):
        # TODO Function can be executed at the same time to calculate a lot of fitness at the same time ? Then result in shared array/dict
        # TODO Maybe try to time it ?
        # Run in parallel (separate threads), RandomAgent and GenAgent(BT) until winner is decided

        p = self.params

        fitness_l = []
        print("\nNew tree")
        for i in range(p.fitness_runs):
            # TODO Try to change seed between runs
            print("Playing a game")
            game_state = self.play_game(
                enemy, btreeA=enemy_btree, btreeB=btree)

            # while(game_state == None):
            #    game_state = self.play_game(IdleAgent, GenAgent, btreeB=btree)

            fitness = p.base_fitness
            if(enemy_btree):
                fitness = enemy_btree.fitness

            # Maybe number of bombs left / placed ?
            tick_n = game_state["tick"]

            if game_state['winning_agent_id'] == "b":
                print("It's a win !")
                unit_left = len([unit for unit in game_state['unit_state'].values(
                ) if unit["agent_id"] == "b" and unit["hp"] > 0])
                fitness += int(200*unit_left*exp(-1/400*tick_n))
            else:
                print("Agent lost...")
                enemy_unit_left = len([unit for unit in game_state['unit_state'].values(
                ) if unit["agent_id"] == "a" and unit["hp"] > 0])
                fitness += int(-200*enemy_unit_left*exp(-1/400*tick_n))

            # Maybe also apply a malus when there's too much nodes in the BTree for example > 20 nodes apply e^-(n-20)
            node_n = btree.number_of_nodes()
            fitness *= exp(-(node_n-p.max_nodes_before_penalty)
                           ) if node_n > p.max_nodes_before_penalty else 1
            fitness = int(fitness) if fitness > 0 else 0
            print(f"Fitness : {fitness}")
            fitness_l.append(fitness)

            # Maybe define function to be lighter
            print("Saving replay...")
            game_id = game_state["game_id"]
            path = Path(
                f'./logs/{str(self.id)}/replays/replay_{str(game_id)}.json')
            path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copyfile(r'..\logs\replay.json', path)

            file = Path(
                f"./logs/{str(self.id)}/replays/{fitness}_{game_id}.txt")
            file.parent.mkdir(exist_ok=True, parents=True)

            file = file.open("w")

            file.write("game_id("+str(game_id)+")\n")
            file.write(enemy.name+" ("+str(enemy_btree.fitness)+")\n"+enemy_btree.tree_to_json()+"\n"
                       if enemy == GenAgent else enemy.name+"\n")
            file.write("GenAgent("+str(fitness)+")\n" +
                       btree.tree_to_json()+"\n")

        btree.fitness = mean(fitness_l)

    def play_game(self, agentA, btreeA=None, btreeB=None):
        server = GP.start_server()
        time.sleep(2)
        manager = Manager()
        return_list = manager.list()

        argsA = (btreeA.tree_to_json(), "agentA",
                 ) if agentA == GenAgent else ("agentA",)
        argsB = (btreeB.tree_to_json(), "agentB", return_list)

        processAgentA = Process(
            target=agentA, args=argsA)  # TODO change args if enemy is of type GenAgent
        processAgentB = Process(
            target=GenAgent, args=argsB)

        processAgentA.start()
        processAgentB.start()

        processAgentA.join()
        processAgentB.join()

        server.terminate()

        if len(return_list) == 0 or return_list[0] == None or return_list[0].get("winning_agent_id") == None:
            print("An error happened, restarting the game")
            print(return_list)
            return self.play_game(agentA, btreeA, btreeB)

        return return_list[0]

    def crossover_pop(self, population):
        # crossover_rate
        print(f"Crossing population")
        offsprings = []

        for tree in population:
            if random() < self.params.co_rate:
                offsprings.append(copy.deepcopy(tree))
        if len(offsprings) % 2 == 1:
            offsprings = offsprings[:-1]

        for i in range(0, len(offsprings), 2):
            BTree.crossover(offsprings[i], offsprings[i+1])

        return offsprings

    def mutate_pop(self, population):
        print(f"Mutating population")

        p = self.params
        offsprings = []

        for tree in population:
            offspring = copy.deepcopy(tree)
            to_mutate = offspring.nodes_to_mutate()
            if len(to_mutate) > 0:
                for node in to_mutate:
                    offspring.mutate(node, p.mut_comp_swap, p.mut_comp_add,
                                     p.mut_comp_remove, p.mut_leaf_swap, p.mut_leaf_remove)
                offsprings.append(offspring)

        return offsprings

    def select_pop(self, population, offsprings):
        print(f"Selecting population")
        new_pop = []
        p = self.params
        all = population + offsprings

        def x(b): return b.fitness
        all.sort(reverse=True, key=x)

        if p.elite_selection:
            num_elite = max(1, int(p.pop_size*p.elite_per))
            new_pop = all[:num_elite]

        # Fitness proportionate selection

        if all:
            total_fitness = sum([tree.fitness for tree in all])

            cumulative_probs = []
            cumulative_probs.append(all[0].fitness / total_fitness)
            for i in range(1, len(all)):
                cumulative_probs.append(cumulative_probs[i-1] +
                                        all[i].fitness / total_fitness)

            for i in range(p.pop_size - len(new_pop)):
                num = random()
                for i in range(len(cumulative_probs)):
                    if cumulative_probs[i] >= num:
                        new_pop.append(copy.deepcopy(all[i]))
                        break

        return new_pop

    def export_gen(self, population, gen_count):
        print(f"Exporting generation...")
        output_file = Path(f"./logs/{self.id}/gen/gen_{gen_count}.txt")
        output_file.parent.mkdir(exist_ok=True, parents=True)

        def x(b): return b.fitness
        population.sort(reverse=True, key=x)

        gen_fitness = sum([tree.fitness for tree in population])

        output_file = output_file.open("w")

        output_file.write(f"{gen_fitness}\n")

        for indiv in population:
            output_file.write(str(indiv))

        output_file.close()

        return


if __name__ == "__main__":
    GP().run()
