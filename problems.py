import operator
import itertools


def nand(x, y):
    return not (x and y)


def nor(x, y):
    return not (x or y)


def protected_division(numerator, denominator):
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return numerator

binary_operators = [operator.or_, operator.and_, nand, nor]
regression_operators = [operator.add, operator.sub,
                        operator.mul, protected_division]


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
        return score


def problem_attributes(range_method, operators, max_arity):
    def wrapper(wraps):
        wraps.range = range_method
        wraps.operators = operators
        wraps.max_arity = max_arity
        return wraps
    return wrapper


def binary_range(config):
    return itertools.product((0, 1), repeat=config['input_length'])


def float_range(config):
    step = (config['max'] - config['min']) / (float(config['samples']) - 1)
    return [x * step + config['min'] for x in range(config['samples'])]


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


@problem_attributes(float_range, regression_operators, 2)
def koza(inputs):
    x = inputs[0]
    return [x ** 6 - 2 * x ** 4 + x ** 2]
