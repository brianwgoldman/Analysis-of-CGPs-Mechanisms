'''
Defines each of the benchmark problems used as well as the function sets
for those problems.
'''
import operator
import itertools
import random
import math


def nand(x, y):
    '''
    Simple Nand function for inclusion in function sets.
    '''
    return not (x and y)


def nor(x, y):
    '''
    Simple Nor function for inclusion in function sets.
    '''
    return not (x or y)


def protected(function):
    '''
    Decorator that ensures decorated functions always have a valid output.
    If an exception occurs or infinity is returned, the first argument of the
    function will be returned.

    Parameters:

    - ``function``: The function to be decorated.
    '''
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
    '''
    Decorator used to make functions take any number of inputs while only
    using the first ``desired`` number of arguments.  For example, you can
    pass 10 arguments to a function that takes only 1 if ``desired=1`` and
    the first of the arguments will actually be used.

    Parameters:

    - ``desired``: The actual arity of the wrapped function.
    '''
    def wrap(function):
        def inner(*args):
            return function(*args[:desired])
        inner.__name__ = function.__name__
        return inner
    return wrap

# Standard lists of operators for different problems to use
binary_operators = [operator.or_, operator.and_, nand, nor]
regression_operators = [operator.add, operator.sub,
                        operator.mul, operator.div]

#for unary in [math.sin, math.cos, math.exp, math.log]:
#    regression_operators.append(arity_controlled(1)(unary))

# Ensures all regression operators are numerically protected
regression_operators = [protected(op) for op in regression_operators]


class Problem(object):
    '''
    Object used to store training input values and expected output values
    which are used in evaluating individuals.
    '''
    def __init__(self, problem_function, config):
        '''
        Create a new problem.

        Parameters:

        - ``problem_function``: The ground truth function that maps input
          values to output values.  Should be decorated with the
          ``problem_attributes`` decorator.
        - ``config``: A dictionary containing the configuration information
          required to fully initialize the problem.  Should include values
          for:

          - Any configuration information required to construct the problem
            range.
          - ``epsilon``: The amount of allowed error on each test.
        '''
        self.training = [(inputs, problem_function(inputs))
                         for inputs in problem_function.range(config)]
        self.epsilon = config['epsilon']

    def get_fitness(self, individual):
        '''
        Return the fitness of an individual as applied to this problem.

        Parameters:

        - ``individual``: The individual to be evaluated.
        '''
        score = 0
        for inputs, outputs in self.training:
            answers = individual.evaluate(inputs)
            # Finds the average number of outputs more than epsilon away from
            # the correct output
            score += (sum(float(abs(answer - output) > self.epsilon)
                          for answer, output in zip(answers, outputs))
                      / len(outputs))
        # Returns the percentage of correct answers
        return 1 - (score / float(len(self.training)))


def problem_attributes(range_method, operators, max_arity):
    '''
    Decorator that adds attributes to problem functions.

    Parameters

    - ``range_method``: The function used to generate training input values.
    - ``operators``: The list of valid operators on this problem.
    - ``max_arity``: The maximum arity of all operators.
    '''
    def wrapper(wraps):
        wraps.range = range_method
        wraps.operators = operators
        wraps.max_arity = max_arity
        return wraps
    return wrapper


def binary_range(config):
    '''
    Given a dictionary specifying the ``input_length``, returns all binary
    values of that length.
    '''
    return itertools.product((0, 1), repeat=config['input_length'])


def float_samples(config):
    '''
    Returns random samples of the input space.

    Parameters:

    - ``config``: A dictionary containing information about the input space.
      - ``min``: The minimum valid value in the space.
      - ``max``: The maximum valid value in the space.
      - ``input_length``: The number of input variables.
      - ``samples``: The number of samples to draw.
    '''
    return ([random.uniform(config['min'], config['max'])
             for _ in xrange(config['input_length'])]
            for _ in xrange(config['samples']))


def float_range(config):
    '''
    Returns a incremental range of a floating point value.  Like range() for
    floats.

    Parameters:

    - ``config``: A dictionary containing information about the input space.
      - ``min``: The minimum valid value in the space.
      - ``max``: The maximum valid value in the space.
      - ``step``: The distance between sample points.
    '''
    counter = 0
    while True:
        value = counter * config['step'] + config['min']
        if value > config['max']:
            break
        yield value
        counter += 1


def n_dimensional_grid(config):
    '''
    Returns a multidimensional grid of points in the input space.

    Parameters:

    - ``config``: A dictionary containing information about the input space.
      - All configuration information required by ``float_range``.
      - ``input_length``: How many dimensions are in the input space.
    '''
    return itertools.product(float_range(config),
                             repeat=config['input_length'])


@problem_attributes(binary_range, binary_operators, 2)
def even_parity(inputs):
    '''
    Return the even parity of a list of boolean values.
    '''
    return [(sum(inputs) + 1) % 2]


@problem_attributes(binary_range, binary_operators, 2)
def binary_multiply(inputs):
    '''
    Return the result of performing a binary multiplication of the first half
    of the inputs with the second half.  Will always have the same number of
    output bits as input bits.
    '''
    # convert the two binary numbers to integers
    joined = ''.join(map(str, inputs))
    middle = len(joined) / 2
    a, b = joined[:middle], joined[middle:]
    # multiply the two numbers and convert back to binary
    multiplied = bin(int(a, 2) * int(b, 2))[2:]
    # pad the result to have enough bits
    extended = multiplied.rjust(len(inputs), '0')
    return map(int, extended)


@problem_attributes(float_samples, regression_operators, 2)
def koza_quartic(inputs):
    '''
    Return the result of Koza-1 on the specified input.  Expects the input
    as a single element list and returns a single element list.
    '''
    x = inputs[0]
    return [x ** 4 + x ** 3 + x ** 2 + x]


@problem_attributes(n_dimensional_grid, regression_operators, 2)
def pagie(inputs):
    '''
    Returns the result of Pagie-1 on the specified inputs.
    '''
    x, y = inputs
    return [1.0 / (1 + x ** -4) + 1.0 / (1 + y ** -4)]


def single_bit_set(config):
    '''
    Creates the list of all possible binary strings of specified length
    with exactly one set bit.  ``config`` should specify the ``input_length``.
    '''
    return [map(int, '1'.rjust(i + 1, '0').ljust(config['input_length'], '0'))
            for i in range(config['input_length'])]


@problem_attributes(single_bit_set, binary_operators, 2)
def binary_encode(inputs):
    '''
    Returns the binary encoding of which input line contains a one.
    '''
    oneat = inputs.index(1)
    binary = bin(oneat)[2:]
    width = math.log(len(inputs), 2)
    return map(int, binary.zfill(int(width)))


@problem_attributes(binary_range, binary_operators, 2)
def binary_decode(inputs):
    '''
    Returns a 1 on the output line specified by the binary input index
    '''
    combined = ''.join(map(str, inputs))
    width = 2 ** len(inputs)
    base = [0] * width
    base[int(combined, 2)] = 1
    return base


@problem_attributes(binary_range, binary_operators, 2)
def mux(inputs):
    '''
    Uses the first k bits as a selector for which of the remaining bits to
    return.
    '''
    k = int(math.log(len(inputs), 2))
    index = int(''.join(map(str, inputs[:k])), 2) + k
    return [inputs[index]]


@problem_attributes(binary_range, binary_operators, 2)
def demux(inputs):
    '''
    Returns the last input bit on the output line specified by the binary
    index encoded on all inputs except the last bit.
    '''
    k = int(math.log(len(inputs) - 1, 2))
    index = int(''.join(map(str, inputs[:k])), 2) + k
    return [inputs[index]]
