from itertools import izip


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
