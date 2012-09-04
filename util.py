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
