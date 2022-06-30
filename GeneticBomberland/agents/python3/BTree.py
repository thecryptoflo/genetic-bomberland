import json
import copy
from random import random, randint, randrange, shuffle
from py_trees.trees import BehaviourTree
from py_trees.display import ascii_tree
from py_trees.composites import Selector, Sequence
from behaviors.SimpleActions import Idle, MoveUp, MoveDown, MoveLeft, MoveRight, PlaceBomb, DetonateLastBomb
from behaviors.SimpleConditions import HealthLow, EnemyClose, InDanger
from behaviors.ComplexActions import AttackEnemy, MoveToSafePlace

# For Behavior Tree Building, maybe setup in Enum Class
# Maybe array of Classes if possible or array of string
# In all the cases, TODO BT to string and string to BT util class
CONTROL_NODES = [Selector, Sequence]  # SEQUENCE, FALLBACK (and PARALLEL)
NECESSARY_NODES = [MoveToSafePlace]  # [MoveUp, MoveDown, MoveLeft, MoveRight]
#BACK_UP_NODES = [MoveToSafePlace]
ACTION_NODES = NECESSARY_NODES + [Idle, PlaceBomb, DetonateLastBomb,
                                  AttackEnemy]  # SimpleActions and ComplexActions
# Conditions : SimpleConditions and ComplexConditions ?
CONDITION_NODES = [HealthLow, EnemyClose, InDanger]
LEAF_NODES = ACTION_NODES + CONDITION_NODES  # ACTION and CONDITION nodes
BEHAVIOURS = CONTROL_NODES + LEAF_NODES

DICT_TXT_TO_TYPE = {node().name: node for node in BEHAVIOURS}


class BTree(BehaviourTree):
    def __init__(self, root=None):
        self.fitness = None
        super(BTree, self).__init__(root if root else Selector())

    def random_node(self):
        i = randrange(self.number_of_nodes()-1)
        j = 0
        parent_control_nodes = [self.root]
        for node in parent_control_nodes:
            for child in node.children:
                if j == i:
                    return child
                elif len(child.children) > 0:
                    parent_control_nodes.append(child)
                j += 1

    def nodes_to_mutate(self):
        nodes = []
        c = self.number_of_nodes() - 1  # We do not consider the root node

        parent_control_nodes = [self.root]
        for node in parent_control_nodes:
            for child in node.children:
                if random() < 1/c:
                    nodes.append(child)
                elif len(child.children) > 0:
                    parent_control_nodes.append(child)

        return nodes

    def mutate(self, node, comp_swap, comp_add, comp_remove, leaf_swap, leaf_remove):
        num = random()
        if type(node) in CONTROL_NODES:
            if num < comp_swap:
                possible_nodes = copy.deepcopy(CONTROL_NODES)
                possible_nodes.remove(type(node))
                new_node = possible_nodes[randrange(len(possible_nodes))]()
                BTree.associate(new_node, node)
                node.parent.replace_child(node, new_node)
            elif num < comp_add:
                child = LEAF_NODES[randrange(len(LEAF_NODES))]()
                node.insert_child(child, randrange(len(node.children)))
            else:
                if node.parent != self.root:
                    if len(node.parent.children) == 1:
                        node.parent.parent.remove_child(node.parent)
                    else:
                        node.parent.remove_child(node)
        else:
            if num < leaf_swap:
                possible_nodes = copy.deepcopy(LEAF_NODES)
                possible_nodes.remove(type(node))
                new_node = possible_nodes[randrange(len(possible_nodes))]()
                node.parent.replace_child(node, new_node)
            else:
                if node.parent != self.root:
                    if len(node.parent.children) == 1:
                        node.parent.parent.remove_child(node.parent)
                    else:
                        node.parent.remove_child(node)

    def crossover(tree_1, tree_2):
        subtree_1 = tree_1.random_node()
        parent_id_1 = subtree_1.id
        subtree_1_c = type(subtree_1)()
        BTree.associate(subtree_1_c, subtree_1)

        subtree_2 = tree_2.random_node()
        parent_id_2 = subtree_2.id
        subtree_2_c = type(subtree_2)()
        BTree.associate(subtree_2_c, subtree_2)

        tree_1.replace_subtree(parent_id_1, subtree_2_c)
        tree_2.replace_subtree(parent_id_2, subtree_1_c)

    def random_btree(max_depth, max_child_per_node, control_node_per):
        root = Selector()  # CONTROL_NODES[randrange(len(CONTROL_NODES))]()
        btree = BTree(root)
        depth = 1
        parent_control_nodes = [root]
        while parent_control_nodes:
            depth += 1
            current_control_nodes = []
            for parent in parent_control_nodes:
                for i in range(randint(2, max_child_per_node)):
                    if depth < max_depth and random() < control_node_per:
                        node = CONTROL_NODES[randrange(
                            len(CONTROL_NODES))]()
                        current_control_nodes.append(node)
                    else:
                        if btree.is_valid():
                            node = LEAF_NODES[randrange(
                                len(LEAF_NODES))]()
                        else:
                            node = NECESSARY_NODES[randrange(
                                len(NECESSARY_NODES))]()
                    parent.add_child(node)
            parent_control_nodes = current_control_nodes

        # Maybe use a while instead of
        return btree if btree.is_valid() else BTree.random_btree(max_depth, max_child_per_node, control_node_per)

    def is_valid(self):
        # We explore BT's nodes and check if there's at least the basic actions to win (Movement ones)
        leaf_node_types = [
            type(node) for node in self.root.iterate() if type(node) in LEAF_NODES]
        # or any(node_type in BACK_UP_NODES for node_type in leaf_node_types)
        return all(node_type in leaf_node_types for node_type in NECESSARY_NODES)

    def number_of_nodes(self):
        return sum(1 for _ in self.root.iterate())
    # Maybe method, fix tree can be useful to make a BTree valid (again)

    def tree_to_json(self, indent=4):
        btree_dict = {}
        btree_dict[self.root.name+"0"] = BTree.b_to_dict(self.root)
        return json.dumps(btree_dict, indent=indent)

    def b_to_dict(behaviour):
        if type(behaviour) in CONTROL_NODES:
            b_dict = {}
            for idx, child in enumerate(behaviour.children):
                b_dict[child.name+str(idx)] = BTree.b_to_dict(child)
            return b_dict
        else:
            return []  # in some case maybe params here ?

    def tree_from_json(json_btree):
        b_dict = json.loads(json_btree)
        # Take the only key at this depth and remove the index used to prevent dup keys
        root_key = list(b_dict.keys())[0]
        root = DICT_TXT_TO_TYPE[root_key[:-1]]()

        BTree.dict_to_b(root, b_dict[root_key])

        return BTree(root)

    def dict_to_b(parent, dict):
        for key in dict.keys():
            node_type = DICT_TXT_TO_TYPE[key[:-1]]
            if node_type in CONTROL_NODES:
                node = node_type()
                BTree.dict_to_b(node, dict[key])
            else:
                # If params needed, they can be reached with dict[key]
                node = node_type()

            parent.add_child(node)

    def __deepcopy__(self, memo):
        root = type(self.root)()
        BTree.associate(root, self.root)
        tree = BTree(root)
        tree.fitness = self.fitness
        return tree

    def associate(copy, parent):
        for child in parent.children:
            # If behavior with params, implement here fetching
            child_copy = type(child)()
            copy.add_child(child_copy)
            BTree.associate(child_copy, child)

    def __str__(self):
        tree = self.tree_to_json()
        return f'BTree({self.fitness})\n{tree}\n'


if __name__ == "__main__":
    tree_1 = BTree.random_btree(3, 4, 0.2)
    tree_2 = BTree.random_btree(3, 4, 0.2)
    print(ascii_tree(tree_1.root))
    tree_1.mutate(0.3, 0.7, 1.0, 0.5, 0.5)
    print(ascii_tree(tree_1.root))
