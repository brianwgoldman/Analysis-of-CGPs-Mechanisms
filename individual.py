import random
import copy
from functools import partial
from util import diff_count


def reset_mutation(data, rate, generate):
    for index in range(len(data)):
        if random.random() < rate:
            data[index] = generate()


class Node(object):
    def __init__(self, max_arity, function_list, input_length, prev_nodes):
        self.random_connection = partial(random.randint,
                                         - input_length, prev_nodes - 1)
        self.connections = [self.random_connection() for _ in range(max_arity)]
        self.function = random.choice(function_list)
        self.function_list = function_list

    def mutate(self, rate):
        reset_mutation(self.connections, rate, self.random_connection)

        if random.random() < rate:
            self.function = random.choice(self.function_list)


class Individual(object):
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list):
        self.random_output = partial(random.randint, -input_length,
                                     graph_length - 1)
        self.input_length = input_length
        self.nodes = [Node(max_arity, function_list, input_length, index)
                      for index in range(graph_length)]
        self.outputs = [self.random_output() for _ in range(output_length)]
        self.determine_active_nodes()

    def make_scratch(self):
        return [None] * (len(self.nodes) + self.input_length)

    def determine_active_nodes(self):
        self.active = set(self.outputs)

        for i, node in enumerate(reversed(self.nodes)):
            index = len(self.nodes) - i - 1
            if index in self.active:
                for connection in node.connections:
                    self.active.add(connection)
        self.active = sorted(self.active)
        self.active = [acting for acting in self.active if acting >= 0]

    def evaluate(self, inputs, scratch):
        # loads the inputs in reverse at the end of the array
        scratch[-len(inputs):] = inputs[::-1]
        for index in self.active:
            working = self.nodes[index]
            args = [scratch[conn] for conn in working.connections]
            scratch[index] = working.function(*args)
        print scratch
        return [scratch[output] for output in self.outputs]

    def mutate(self, rate):
        mutant = copy.deepcopy(self)
        for node in mutant.nodes:
            node.mutate(rate)

        reset_mutation(mutant.outputs, rate, mutant.random_output)
        mutant.determine_active_nodes()
        return mutant

    def asymmetric_phenotypic_difference(self, other):
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
