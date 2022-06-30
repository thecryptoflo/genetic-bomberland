# Python Implementation of Genetic Programming applied to Behavior Trees in order to create an agent for Bomberland

This repo is based on CoderOneHQ starter kits and engine for the game Bomberland available in the original repo here https://github.com/CoderOneHQ/bomberland

## About

The goal of this project was to make a fit agent for the game Bomberland by CoderOne using Genetic Programming applied to Behaviour Trees that controls how the agent plays.
You can find the explanations and informations about the project, theorical choices and overview of the implementation, in the report "PROJECT-Genetic Programming and Behaviour Trees" available at repo root.

## Usage

### Quick Intro

In this project I removed all the useless folders available in the original repository to keep it light apart from the engine made in TypeScript because I think one of the way of making this implementation more performant would be to directly launch the node server for fitness calculations.

### BTree and Behaviours

I assume you're familiar with the notions of Behaviour Trees and Behaviours after reading the report at this point.
The class Btree.py inside the folder `GeneticBomberland/agents/python3` inherits from py_trees' BehaviourTree class and additionally stores the fitness of the BTree.
The following utility functions and methods have then been added :

- `random_btree` : Function generating a valid random BTree following the grow method, useful to initialize the population
- `crossover` : Function accepting 2 parent BTrees and crossing them over into two offsprings. Uses `random_node` to select the crossover point of each BTree
- `mutate` : Method to mutate a specific node selected precedently with the `nodes_to_mutate` method. Accept parameters to control the nature of the mutation depending on node type
- `tree_to_json` and `tree_from_json`: A Method and a function useful to export and import the trees to and from a json file. Used to save generations as well as serializing the BTree to pass it to the child process
- `__deepcopy__` and `associate` : Two functions used to deepcopy a Btree. Note that a deep copy could also be realized by serializing and deserializing a Btree but that would take more time.

In the BTree class you can also find some globally defined arrays containing the different available Behaviours that can be used inside a BTree:

- `CONTROL_NODES` : List of composite nodes available
- `NECESSARY_NODES` : List of leaf nodes where every node that it contains needs to be present in order for a BTree to be valid
- `ACTION_NODES` : Among the leaf nodes, contains the ones that send a move to the server
- `CONDITIONS_NODES` : Among the leaf nodes, contains the ones that don't send any move, and are usefull through the tick type they return (SUCCESS, RUNNING, FAILURE)
- `LEAF_NODES` : Contains the action and conditions nodes available to be used
- `BEHAVIOURS` : List containing all the behaviours made available by the previous arrays

The different behaviours code can be found inside the `behaviors` folder.
In `SQUELETON.py`, you can find the template provided by py_trees for a behaviour.
In `SimpleActions` and `ComplexActions` are defined the actions. An action is considered simple if when it succeeds always send the same move. Complex actions are more high-level.
In `SimpleConditions` are defined some basic conditions. In the same model as actions a `ComplexConditions` class could be created in order to better classify the different type of condition behaviours.

### Agents

In the folder GeneticBomberland/agents/python3 can be found the following class representing agents that can connect to the server and play a game

- `agent.py` is the default agent that plays randomly provided by the starter kit
- `random_agent.py` is the adaptation of the previous agent in order for it to be used with our implementation
- `idle_agent.py` is an agent that can be used with our implementation and that basically does not do anything (idleing)
- `gen_agent.py` is the agent controlled by a provided BTree and which can report game final state when it is finished
- `admin.py` is an admin agent which isn't a player but that can ask the server for the game to be reset. Not used in the current implementation but can be useful if the server is only launch one time and we only reset the game between matches for BTrees' fitness calculations.

The file `game_state.py` contains different utility method to interact with the server and the game_state. It's used by the agent but also by the behaviours that are directly sending moves to the server if it's possible.

### Logs

Each time a game is played, the server saves a replay in the file `agents/logs/replay.json`. We then copy it, rename it inside `agents/python3/logs/{GP_id}/replays/replay_{game_id}.json` and store some metadata about the match `...replays/{gen_agent_game_fitness}_{game_id}.txt` such as both agent (and potentially BTrees that played the game). First is logged Agent A and then Agent B.
In the folder `agents/python3/logs/{GP_id}/` can also be found :

- `params.json` file where params for current GP execution are logged
- `gen/` folder where every generation is saved

### Genetic Programming-based Algorithm

First in `genetic_programming.py` we can find a dataclass called GpParams that is used to hold all the different parameters used in the GP class execution.

Then we can find the GP (GeneticProgramming) class, core of the implementation, and used to run the developped genetic programming algorithm.
As described in the report, the following method can be found :

- `run` : Main algorithm loop (described in the report)
- `initialize_pop` : Population initialization
- `evaluate_pop` and `fitness` : Methods to evaluate the population fitness. In fitness method `play_game` is called and then the fitness is calculated as well as copying the replay.json and metadatas at the right place in the logs.
- `play_game` : It launches the server with the `start_server` function (launches docker container with environment variables defined in `GeneticBomberland/docker-compose.yml`, see CoderOne doc for more informations). Then it spawns agents in subprocesses with the BTreses if necessary. Then returns the final game_state when finished.
- `crossover_pop`, `mutate_pop` and `select_pop`: Main genetic methods at the core of Genetic Programming and described in the report.
- `export_gen` : export the current generation to the correct folder in `python3/logs/`. It also contains the population fitness in the first line.

Some code is also in place inside fitness calculation, agents and game_state in order when connection bugs and matches bugs happens in order to make the code more resilient and not crash.
