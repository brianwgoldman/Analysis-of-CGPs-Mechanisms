import random
import copy
import sys
from functools import partial
from util import diff_count, binary_counter


def reset_mutation(data, rate, generate):
    for index in range(len(data)):
        if random.random() < rate:
            data[index] = generate()


class Node(object):
    def __init__(self, max_arity, function_list, input_length, prev_nodes):
        self.random_connection = partial(random.randint, -input_length,
                                         prev_nodes - 1)
        self.connections = [self.random_connection() for _ in range(max_arity)]
        self.function = random.choice(function_list)
        self.function_list = function_list

    def mutate(self, rate):
        reset_mutation(self.connections, rate, self.random_connection)

        if random.random() < rate:
            self.function = random.choice(self.function_list)


class Individual(object):
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list, **_):
        self.random_output = partial(random.randint, -input_length,
                                     graph_length - 1)
        self.input_length = input_length
        self.nodes = [Node(max_arity, function_list, input_length, index)
                      for index in range(graph_length)]
        # TODO According to crossover.pdf, outputs initialize to last nodes
        self.outputs = [self.random_output() for _ in range(output_length)]
        self.determine_active_nodes()
        # If memory problems persist, make this globally shared
        self.scratch = [None] * (len(self.nodes) + self.input_length)
        self.fitness = -sys.maxint

    def determine_active_nodes(self):
        self.active = set(self.outputs)

        for i, node in enumerate(reversed(self.nodes)):
            index = len(self.nodes) - i - 1
            if index in self.active:
                for connection in node.connections:
                    self.active.add(connection)
        self.active = sorted(self.active)
        self.active = [acting for acting in self.active if acting >= 0]

    def evaluate(self, inputs):
        # loads the inputs in reverse at the end of the array
        self.scratch[-len(inputs):] = inputs[::-1]
        for index in self.active:
            working = self.nodes[index]
            args = [self.scratch[conn] for conn in working.connections]
            self.scratch[index] = working.function(*args)
        return [self.scratch[output] for output in self.outputs]

    def mutate(self, rate):
        mutant = copy.deepcopy(self)
        for node in mutant.nodes:
            node.mutate(rate)

        reset_mutation(mutant.outputs, rate, mutant.random_output)
        mutant.determine_active_nodes()
        return mutant

    def asym_phenotypic_difference(self, other):
        differences = diff_count(self.outputs, other.outputs)
        for active in self.active:
            differences += diff_count(self.nodes[active].connections,
                                      other.nodes[active].connections)
            differences += (self.nodes[active].function !=
                            other.nodes[active].function)
        return differences

    def __str__(self):
        nodes = ' '.join("%i %s%s" % (index, node.function.__name__,
                         str(node.connections))
                         for index, node in enumerate(self.nodes))
        return nodes + str(self.outputs)

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
    for i in range(100):
        best = Individual(**required)
        for evals, individual in enumerate(generate(required)):
            raw = [abs(individual.evaluate(x)[0] - y) for x, y in tests]
            fit = -sum(raw)
            individual.fitness = fit
            if best < individual:
                best = individual
                print evals, best.fitness
            if evals > 6000 or best.fitness == 0:
                print '\t', evals, best.fitness
                data.append(evals)
                break

    print sum(data) / float(len(data))

import cProfile
cProfile.run("main()", sort=2)
