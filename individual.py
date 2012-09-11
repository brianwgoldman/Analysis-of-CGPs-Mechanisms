import random
import sys
from copy import copy
from util import diff_count, binary_counter


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
        # If memory problems persist, make this globally shared
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
        self.scratch = [None] * (self.graph_length + self.input_length)
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


def constmaker(value):
    def inner(*args, **kwargs):
        return value
    return inner


def protectdiv(num, denom):
    try:
        return float(num) / denom
    except ZeroDivisionError:
        return num


def nor(p, q):
    return not (p or q)


def nand(p, q):
    return not (p and q)

import operator
required = {'graph_length': 4000, 'input_length': 3,
            'output_length': 1, 'max_arity': 2,
            'function_list': [operator.and_, operator.or_, nor, nand],
            'off_size': 4,
            'speed': sys.argv[1],
            'mutation_rate': .02}


def target(z):
    return (sum(z) + 1) % 2


def main():
    xs = list(binary_counter(3))
    ys = map(target, xs)
    tests = zip(xs, ys)

    data = []
    for _ in range(100):
        best = Individual(**required)
        for evals, individual in enumerate(generate(required)):
            raw = [abs(individual.evaluate(x)[0] - y) for x, y in tests]
            fit = -sum(raw)
            individual.fitness = fit
            if best < individual:
                best = individual
                print evals, best.fitness
            if evals >= 5000 or best.fitness == 0:
                print '\t', evals, best.fitness
                data.append(evals)
                break

    print sum(data) / float(len(data)), sum(data)

random.seed(int(sys.argv[2]))
main()
