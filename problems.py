import operator
import itertools
import random
import math


def nand(x, y):
    return not (x and y)


def nor(x, y):
    return not (x or y)


def protected(function):
    def inner(*args):
        try:
            value = function(*args)
            if math.isinf(value):
                return args[0]
            return value
        except (ValueError, OverflowError, ZeroDivisionError):
            return args[0]
    inner.__name__ = function.__name__
    return inner


def arity_controlled(desired):
    def wrap(function):
        def inner(*args):
            return function(*args[:desired])
        inner.__name__ = function.__name__
        return inner
    return wrap

binary_operators = [operator.or_, operator.and_, nand, nor]
regression_operators = [operator.add, operator.sub,
                        operator.mul, operator.div]

for unary in [math.sin, math.cos, math.exp, math.log]:
    regression_operators.append(arity_controlled(1)(unary))

regression_operators = [protected(op) for op in regression_operators]


class Problem(object):
    def __init__(self, problem_function, config):
        self.training = [(inputs, problem_function(inputs))
                         for inputs in problem_function.range(config)]

    def get_fitness(self, individual):
        score = 0
        for inputs, outputs in self.training:
            answers = individual.evaluate(inputs)
            score -= sum(abs(answer - output)
                         for answer, output in zip(answers, outputs))
        return score / float(len(self.training))


def problem_attributes(range_method, operators, max_arity):
    def wrapper(wraps):
        wraps.range = range_method
        wraps.operators = operators
        wraps.max_arity = max_arity
        return wraps
    return wrapper


def binary_range(config):
    return itertools.product((0, 1), repeat=config['input_length'])


def float_samples(config):
    return ([random.uniform(config['min'], config['max'])
             for _ in xrange(config['input_length'])]
            for _ in xrange(config['samples']))


def float_range(config):
    counter = 0
    while True:
        value = counter * config['step'] + config['min']
        if value > config['max']:
            break
        yield value
        counter += 1


def n_dimensional_grid(config):
    return itertools.product(float_range(config),
                             repeat=config['input_length'])


@problem_attributes(binary_range, binary_operators, 2)
def even_parity(inputs):
    return [(sum(inputs) + 1) % 2]


@problem_attributes(binary_range, binary_operators, 2)
def binary_multiply(inputs):
    joined = ''.join(map(str, inputs))
    middle = len(joined) / 2
    a, b = joined[:middle], joined[middle:]
    multiplied = bin(int(a, 2) * int(b, 2))[2:]
    extended = multiplied.rjust(len(inputs), '0')
    return map(int, extended)


@problem_attributes(float_samples, regression_operators, 2)
def koza_quartic(inputs):
    x = inputs[0]
    return [x ** 4 + x ** 3 + x ** 2 + x]


@problem_attributes(n_dimensional_grid, regression_operators, 2)
def paige(inputs):
    x, y = inputs
    return [1.0 / (1 + x ** -4) + 1.0 / (1 + y ** -4)]
