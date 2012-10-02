import random
import sys
from copy import copy
from util import diff_count
import itertools
from collections import defaultdict


class Individual(object):
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list, **_):
        self.node_step = max_arity + 1
        self.input_length = input_length
        self.graph_length = graph_length
        self.function_list = function_list
        self.output_length = output_length
        self.genes = None
        self.genes = [self.random_gene(index) for index in
                      range(graph_length * self.node_step + output_length)]
        self.determine_active_nodes()
        # If memory problems arise, make this globally shared
        self.scratch = [None] * (graph_length + self.input_length)
        self.fitness = -sys.maxint

    def random_gene(self, index):
        node_number = index // self.node_step
        gene_number = index % self.node_step
        if node_number >= self.graph_length:
            node_number = self.graph_length
            gene_number = -1

        if gene_number == 0:
            return random.choice(self.function_list)
        else:
            return random.randint(-self.input_length, node_number - 1)

    def dag_random_gene(self, index):
        node_number = index // self.node_step
        gene_number = index % self.node_step
        if node_number >= self.graph_length:
            node_number = self.graph_length
            gene_number = -1

        if gene_number == 0:
            return random.choice(self.function_list)
        elif gene_number < 0 or not self.genes:
            return random.randint(-self.input_length, node_number - 1)
        else:
            return self.valid_reconnect(node_number)

    def copy(self):
        # WARNING individuals are shallow copied except for things added here
        new = copy(self)
        new.genes = list(self.genes)
        return new

    def connections(self, node_index):
        node_start = self.node_step * node_index
        return self.genes[node_start + 1: node_start + self.node_step]

    def determine_active_nodes(self):
        self.active = set(self.genes[-self.output_length:])

        for node_index in reversed(range(self.graph_length)):
            if node_index in self.active:
                # add all of the connection genes for this node
                self.active.update(self.connections(node_index))
        self.active = sorted([acting for acting in self.active if acting >= 0])

    def dag_determine_active_nodes(self):
        depends_on = defaultdict(set)
        feeds_to = defaultdict(set)
        connected = self.genes[-self.output_length:]
        added = set(connected)
        # find the active nodes
        while connected:
            working = connected.pop()
            if working < 0:
                continue
            for conn in self.connections(working):
                depends_on[working].add(conn)
                feeds_to[conn].add(working)
                if conn not in added:
                    connected.append(conn)
                added.add(conn)
        # find the order in which to evaluate them
        self.active = []
        activatable = [x for x in range(-self.input_length, 0)]

        while activatable:
            working = activatable.pop()
            for conn in feeds_to[working]:
                depends_on[conn].remove(working)
                if len(depends_on[conn]) == 0:
                    activatable.append(conn)
                    self.active.append(conn)

    def evaluate(self, inputs):
        self.scratch[-len(inputs):] = inputs[::-1]
        for node_index in self.active:
            function = self.genes[node_index * self.node_step]
            args = [self.scratch[con] for con in self.connections(node_index)]
            self.scratch[node_index] = function(*args)
        return [self.scratch[output]
                for output in self.genes[-self.output_length:]]

    def mutate(self, rate):
        mutant = self.copy()
        for index in range(len(mutant.genes)):
            if random.random() < rate:
                mutant.genes[index] = mutant.random_gene(index)
        mutant.determine_active_nodes()
        return mutant

    def one_active_mutation(self, _):
        mutant = self.copy()
        while True:
            index = random.randrange(len(mutant.genes))
            newval = mutant.random_gene(index)
            if newval != mutant.genes[index]:
                mutant.genes[index] = newval
                node_number = index // self.node_step
                if (node_number >= self.graph_length or
                    node_number in self.active):
                    break
        mutant.determine_active_nodes()
        return mutant

    def reorder(self):
        depends_on = defaultdict(set)
        feeds_to = defaultdict(set)
        for node_index in range(self.graph_length):
            for conn in self.connections(node_index):
                depends_on[node_index].add(conn)
                feeds_to[conn].add(node_index)
        new_order = {i: i for i in range(-self.input_length, 0)}
        addable = new_order.keys()
        counter = 0
        while addable:
            working = random.choice(addable)
            addable.remove(working)
            for to_add in feeds_to[working]:
                depends_on[to_add].remove(working)
                if len(depends_on[to_add]) == 0:
                    addable.append(to_add)
                    new_order[to_add] = counter
                    counter += 1

        mutant = self.copy()
        for node_index in range(self.graph_length):
            start = new_order[node_index] * self.node_step
            mutant.genes[start] = self.genes[node_index * self.node_step]
            connections = [new_order[conn]
                           for conn in self.connections(node_index)]
            mutant.genes[start + 1:start + self.node_step] = connections
        length = len(self.genes)
        for index in range(length - self.output_length, length):
            mutant.genes[index] = new_order[self.genes[index]]
        mutant.determine_active_nodes()
        return mutant

    def asym_phenotypic_difference(self, other):
        count = diff_count(self.genes[-self.output_length:],
                           other.genes[-self.output_length:])
        for node_index in self.active:
            index = node_index * self.node_step
            count += diff_count(self.connections(node_index),
                                other.connections(node_index))
            count += (self.genes[index] !=
                      other.genes[index])
        return count

    def valid_reconnect(self, node_index):
        dependent = {node_index: True}
        for index in range(-self.input_length, 0):
            dependent[index] = False

        def is_dependent(current):
            if current in dependent:
                return dependent[current]
            for conn in self.connections(current):
                if is_dependent(conn):
                    dependent[current] = True
                    return True
            dependent[current] = False
            return False

        while True:
            # Select a random node that is not dependent on this one
            options = [index for index in
                       range(-self.input_length, self.graph_length)
                       if index not in dependent or not dependent[index]]
            option = random.choice(options)
            if not is_dependent(option):
                return option

    def show_active(self):
        for node_index in self.active:
            node_start = self.node_step * node_index
            print node_index, self.genes[node_start], self.connections(node_index)

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __le__(self, other):
        return self.fitness <= other.fitness


def generate(config):
    if config['dag']:
        Individual.determine_active_nodes = \
        Individual.dag_determine_active_nodes
        Individual.random_gene = \
        Individual.dag_random_gene
    if config['one_active_mutation']:
        Individual.mutate = Individual.one_active_mutation
    parent = Individual(**config)
    yield parent
    while True:
        if config['reorder']:
            parent = parent.reorder()
        mutants = [parent.mutate(config['mutation_rate'])
                   for _ in range(config['off_size'])]
        for index, mutant in enumerate(mutants):
            prev = mutant
            if config['speed'] != 'normal':
                change = parent.asym_phenotypic_difference(mutant)
                if change == 0:
                    if config['speed'] == 'no_reeval':
                        continue
                    if config['speed'] == 'mutate_until_change':
                        while change == 0:
                            prev = mutant
                            mutant = prev.mutate(config['mutation_rate'])
                            change = parent.asym_phenotypic_difference(mutant)
            yield mutant
            if config['speed'] == 'mutate_until_change':
                # If the mutant is strickly worse, use the last equivalent
                mutants[index] = prev if mutant < parent else mutant
        best_child = max(mutants)
        if parent <= best_child:
            parent = best_child


def multi_indepenedent(config):
    collective = itertools.izip(*[generate(config)
                                  for _ in range(config['pop_size'])])
    for next_iterations in collective:
        for next_iteration in next_iterations:
            yield next_iteration
