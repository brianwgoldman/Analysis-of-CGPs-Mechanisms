import random
import copy


class Node(object):
    def __init__(self, max_arity, function_list, prev_nodes):
        self.connections = [random.randint(0, prev_nodes - 1)
                            for _ in range(max_arity)]
        self.function = random.choice(function_list)
        self.prev_nodes = prev_nodes
        self.function_list = function_list

    def mutate(self, rate):
        for i in range(len(self.connections)):
            if random.random() < rate:
                self.connections[i] = random.randint(0, self.prev_nodes - 1)

        if random.random() < rate:
            self.function = random.choice(self.function_list)


class Graph(object):
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list):
        self.function_list = function_list
        self.input_length = input_length
        self.nodes = [Node(max_arity, function_list, index + input_length)
                      for index in range(graph_length)]
        # Consider a better representation for input nodes than "None"
        self.nodes = [None] * input_length + self.nodes
        self.outputs = [random.randint(0, len(self.nodes) - 1)
                        for _ in range(output_length)]
        self.scratch = [None] * len(self.nodes)
        self.determine_active_nodes()

    def determine_active_nodes(self):
        self.active = set(self.outputs)

        for index in range(len(self.nodes) - 1, self.input_length - 1, -1):
            if index in self.active:
                for connection in self.nodes[index].connections:
                    self.active.add(connection)
        self.active = sorted(self.active)[self.input_length:]

    def evaluate(self, inputs):
        self.scratch[:len(inputs)] = inputs
        for index in self.active:
            working = self.nodes[index]
            args = [self.scratch[conn] for conn in working.connections]
            function = self.function_list[working.function_index]
            self.scratch[index] = function(*args)
        return [self.scratch[output] for output in self.outputs]

    def mutate(self, rate):
        mutant = copy.deepcopy(self)
        for node in mutant.graph.nodes:
            node.mutate()

        for index in range(len(self.outputs)):
            if random.random() < rate:
                self.outputs[index] = random.randint(0, len(self.nodes) - 1)

    def __str__(self):
        nodes = ' '.join(self.function_list[node.function_index].__name__ +
                         str(node.connections) for node in self.nodes if node)
        return nodes + str(self.outputs)


class Individual(object):
    def __init__(self, graph_length, input_length, output_length,
                  max_arity, function_list):
        self.graph = Graph(graph_length, input_length, output_length,
                           max_arity, function_list)


