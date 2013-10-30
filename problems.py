'''
Defines each of the benchmark problems used as well as the function sets
for those problems.
'''
from operator import or_, and_, add, sub, mul, div, xor
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


def and_neg_in(x, y):
    return (not x) and y


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
            # Call the function on the arguments
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
binary_operators = [or_, and_, nand, nor]
regression_operators = [add, sub,
                        mul, div]

# for unary in [math.sin, math.cos, math.exp, math.log]:
#    regression_operators.append(arity_controlled(1)(unary))

# Ensures all regression operators are numerically protected
regression_operators = [protected(op) for op in regression_operators]


class Problem(object):
    '''
    The abstract base of a problem
    '''
    def __init__(self, config):
        '''
        Designed to force children of this class to implement this function.
        Children use this function to set up problem specific initialization
        from configuration information.
        '''
        raise NotImplementedError()

    def get_fitness(self, individual):
        '''
        Designed to force children of this class to implement this function.
        Children use this function evaluate an individual and
        return its fitness.
        '''
        raise NotImplementedError()


class Bounded_Problem(object):
    '''
    Base object for any problem with a known set of test cases.  Stores a
    map for all possible inputs to their correct outputs so they only
    have to be evaluated once.
    '''

    def __init__(self, config):
        '''
        Create a new problem.

        Parameters:

        - ``config``: A dictionary containing the configuration information
          required to fully initialize the problem.  Should include values
          for:

          - Any configuration information required to construct the problem
            range.
          - ``epsilon``: The amount of allowed error on each test.
        '''
        self.config = config
        self.training = [(inputs, self.problem_function(inputs))
                         for inputs in self.data_range(config)]
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

    def problem_function(self, _):
        '''
        Designed to force children of this class to implement this function.
        Children use this function to define how to translate an input value
        into an output value for their problem.
        '''
        raise NotImplementedError()


def binary_range(config):
    '''
    Given a dictionary specifying the ``input_length``, returns all binary
    values of that length.
    '''
    return itertools.product((0, 1), repeat=config['input_length'])


def single_bit_set(config):
    '''
    Creates the list of all possible binary strings of specified length
    with exactly one set bit.  ``config`` should specify the ``input_length``.
    '''
    return [tuple(map(int,
                      '1'.rjust(i + 1, '0').ljust(config['input_length'], '0')
                      )
                  )
            for i in range(config['input_length'])]


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


class Binary_Mixin(object):
    '''
    Inheritance mixin useful for setting the class attributes of
    binary problems.
    '''
    data_range = staticmethod(binary_range)
    operators = binary_operators
    max_arity = 2


class Regression_Mixin(object):
    '''
    Inheritance mixin useful for setting the class attributes of
    regression problems.
    '''
    data_range = staticmethod(float_range)
    operators = regression_operators
    max_arity = 2


class Neutral(Problem):
    '''
    Defines the Neutral problem, in which all individuals receive the same
    fitness.  The only operator in this function is 'None', meaning only
    connection genes actually evolve.
    '''
    operators = [None]
    max_arity = 2

    def __init__(self, _):
        '''
        Doesn't require initialization, but must implement.
        '''
        pass

    def get_fitness(self, _):
        '''
        Returns the fitness of passed in individual, which is always 0.
        '''
        return 0


class Even_Parity(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Even Parity problem.
    '''
    def problem_function(self, inputs):
        '''
        Return the even parity of a list of boolean values.
        '''
        return [(sum(inputs) + 1) % 2]


class Binary_Multiply(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Binary Multiplier problem.
    '''
    def problem_function(self, inputs):
        '''
        Return the result of performing a binary multiplication of the first
        half of the inputs with the second half.  Will always have the same
        number of output bits as input bits.
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


class Binary_Multiply_Miller(Binary_Multiply):
    operators = [and_, and_neg_in, xor, or_]


class Binary_Multiply_Torresen(Binary_Multiply):
    operators = [and_, xor]


class Multiplexer(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Multiplexer (MUX) Problem.
    '''
    def problem_function(self, inputs):
        '''
        Uses the first k bits as a selector for which of the remaining bits to
        return.
        '''
        k = int(math.log(len(inputs), 2))
        index = int(''.join(map(str, inputs[:k])), 2) + k
        return [inputs[index]]


class Demultiplexer(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Demultiplexer (DEMUX) Problem.
    '''
    def problem_function(self, inputs):
        '''
        Returns the last input bit on the output line specified by the binary
        index encoded on all inputs except the last bit.
        '''
        k = int(math.log(len(inputs) - 1, 2))
        index = int(''.join(map(str, inputs[:k])), 2) + k
        return [inputs[index]]


class Binary_Encode(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Binary Encode problem.
    '''
    # Set the data range to be all possible inputs with a single set bit.
    data_range = staticmethod(single_bit_set)

    def problem_function(self, inputs):
        '''
        Returns the binary encoding of which input line contains a one.
        '''
        oneat = inputs.index(1)
        binary = bin(oneat)[2:]
        width = math.log(len(inputs), 2)
        return map(int, binary.zfill(int(width)))


class Binary_Decode(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Binary Decode problem.
    '''
    def problem_function(self, inputs):
        '''
        Returns a 1 on the output line specified by the binary input index
        '''
        combined = ''.join(map(str, inputs))
        width = 2 ** len(inputs)
        base = [0] * width
        base[int(combined, 2)] = 1
        return base


class Breadth(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Breadth problem.
    '''
    # Set the data range to be all possible inputs with a single set bit.
    data_range = staticmethod(single_bit_set)
    # Set the list of possible operators to just be OR.
    operators = [or_]

    def problem_function(self, inputs):
        '''
        Returns true as long as at least one input is true.
        '''
        return [sum(inputs) > 0]


class TwoFloor(Bounded_Problem, Binary_Mixin):
    '''
    Defines the Two Floor Problem.
    '''
    # Set the data range to be all possible inputs with a single set bit.
    data_range = staticmethod(single_bit_set)
    # Set the list of possible operators to just be OR.
    operators = [or_]

    def problem_function(self, inputs):
        '''
        Returns a string of bits half as long as the input string, where
        the only set output bit is at the index // 2 of the set input bit.
        '''
        results = [0] * (len(inputs) // 2)
        results[inputs.index(1) // 2] = 1
        return results


class Depth(Problem):
    '''
    Defines the Depth problem.
    '''
    # Set the list of possible operators to just be just min(X, Y) + 1.
    operators = [lambda X, Y: min(X, Y) + 1]
    max_arity = 2

    def __init__(self, config):
        '''
        Saves configuration for use during evaluation.
        '''
        self.config = config

    def get_fitness(self, individual):
        '''
        Returns the fitness of the individual as a percentage of maximum
        fitness.
        '''
        score = individual.evaluate((0,))[0]
        return score / float(self.config['graph_length'])


class Flat(Problem):
    '''
    Defines the Flat problem, in which all individuals receive fitness
    based on how many connection genes are connected to the input.
    The only operator in this function is 'None', meaning only
    connection genes actually evolve.
    '''
    operators = [None]
    max_arity = 2

    def __init__(self, _):
        '''
        Doesn't require initialization, but must implement.
        '''
        pass

    def get_fitness(self, individual):
        '''
        Returns the percentage of connection genes connected to the input.
        '''
        correct, total = 0, 0
        for gene in individual.genes:
            if gene is not None:
                if gene < 0:
                    correct += 1
                total += 1
        return correct / float(total)


class Novel(Problem, Binary_Mixin):
    '''
    Defines the Novel problem, which evaluates individuals based on how many
    unique footprints the individual can create.
    '''
    def __init__(self, config):
        complete = float(2 ** 2 ** config['input_length'])
        self.best = float(min(complete, config['graph_length']))

    def get_fitness(self, individual):
        for inputs in binary_range(self.config):
            individual.evaluate(inputs)
        return len(set(individual.footprint)) / self.best


class Active(Problem):
    '''
    Defines the Active problem, in which all individuals receive fitness
    based on how many active nodes they have.
    The only operator in this function is 'None', meaning only
    connection genes actually evolve.
    '''
    operators = [None]
    max_arity = 2

    def __init__(self, config):
        '''
        Saves configuration for use during evaluation.
        '''
        self.config = config

    def get_fitness(self, individual):
        '''
        Returns the percentage of nodes that are active.
        '''
        return len(individual.active) / float(self.config['graph_length'])


class Koza_1(Bounded_Problem, Regression_Mixin):
    '''
    Defines the Koza-1 problem.
    '''
    def koza_quartic(self, inputs):
        '''
        Return the result of Koza-1 on the specified input.  Expects the input
        as a single element list and returns a single element list.
        '''
        x = inputs[0]
        return [x ** 4 + x ** 3 + x ** 2 + x]


class Pagie_1(Bounded_Problem, Regression_Mixin):
    '''
    Defines the Pagie-1 problem.
    '''
    # Set the data range to be an n dimensional grid.
    data_range = staticmethod(n_dimensional_grid)

    def pagie(self, inputs):
        '''
        Returns the result of Pagie-1 on the specified inputs.
        '''
        x, y = inputs
        return [1.0 / (1 + x ** -4) + 1.0 / (1 + y ** -4)]
