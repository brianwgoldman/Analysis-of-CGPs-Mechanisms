from itertools import izip
from inspect import getargspec
import itertools


def memoize(wraps):
    seen = {}

    def inner(*args):
        try:
            return seen[args]
        except KeyError:
            seen[args] = wraps(*args)
            return seen[args]
    return inner


def arity_control(number):
    def wrap(wrapped):
        def at_call(*args):
            if len(args) != number:
                raise TypeError("Arity control requires %i arguments, got %i" %
                                (number, len(args)))
            return wrapped(*args)
        at_call.arity = number
        return at_call
    return wrap


def diff_count(data1, data2):
    return sum(x != y for x, y in izip(data1, data2))


def overloaded(wraps):
    required = getargspec(wraps)[0]

    def inner(*args, **kwargs):
        used = dict((key, kwargs[key]) for key in required[len(args):]
                    if key in kwargs)
        return wraps(*args, **used)
    return inner


def binary_counter(bits):
    '''
    Creates a generator that will count through all possible values for a set
    number of bits.  Returned in counting order.  For instance,
    ``binaryCounter(3)`` will yield, 000, 001, 010, 011 ... 110, 111.

    Parameters:

    - ``bits`` The number of bits in the binary counter.
    '''
    return itertools.product((0, 1), repeat=bits)
