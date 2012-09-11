from itertools import izip
import json
import os
import math


def diff_count(data1, data2):
    return sum(x != y for x, y in izip(data1, data2))


def load_configurations(filenames, file_method=open):
    result = {}
    for filename in filenames:
        with file_method(filename, 'r') as f:
            result.update(json.load(f))
    return result


def save_configuration(filename, data, file_method=open):
    with file_method(filename, 'w') as f:
        json.dump(data, f)


def save_list(filename, data, file_method=open):
    with file_method(filename, 'w') as f:
        f.write('[' + os.linesep)
        for lineNumber, line in enumerate(data):
            json.dump(line, f)
            if lineNumber != len(data) - 1:
                f.write(",")
            f.write(os.linesep)
        f.write(']' + os.linesep)


def meanstd(data):
    '''
    Returns the mean and standard deviation of the given data.

    Parameters:

    - ``data``: The data to find the mean and standard deviation of.
    '''
    try:
        mean = float(sum(data)) / len(data)
        std = math.sqrt(sum([(value - mean) ** 2 for value in data])
                        / len(data))
        return mean, std
    except (ZeroDivisionError, TypeError):
        return 0, 0
