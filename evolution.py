import random
import sys
from copy import copy
from util import diff_count


class Individual(object):
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list, **_):
        self.node_step = max_arity + 1
        self.input_length = input_length
        self.graph_length = graph_length
        self.function_list = function_list
        self.output_length = output_length
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

    def reorder(self):
        dependencies = {node_index: set(self.connections(node_index))
                        for node_index in range(self.graph_length)}
        added = set(range(-self.input_length, 0))

        def available():
            return [node_index
                    for node_index, depends_on in dependencies.iteritems()
                    if depends_on <= added]
        new_order = {i: i for i in range(-self.input_length, 0)}
        counter = 0
        while dependencies:
            #to_add = random.choice(available())
            choices = available()
            to_add = random.choice(choices)
            new_order[to_add] = counter
            counter += 1
            del dependencies[to_add]
            added.add(to_add)

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

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __le__(self, other):
        return self.fitness <= other.fitness


def generate(config):
    parent = Individual(**config)
    yield parent
    while True:
        mutants = [parent.mutate(config['mutation_rate'])
                   for _ in range(config['off_size'])]
        if config['reorder']:
            mutants = [mutant.reorder() for mutant in mutants]
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
