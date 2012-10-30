from itertools import izip, cycle
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


def find_median(data):
    ordered = sorted(data)

    length = len(data)
    middle = length // 2
    if length % 2 == 1:
        return ordered[middle]
    else:
        return (ordered[middle] + ordered[middle - 1]) / 2.0


def median_deviation(data, median=None):
    if median is None:
        median = find_median(data)
    return  median, find_median([abs(x - median) for x in data])


def resample_probability(i, k, n):
    n = float(n)
    not_i = (n - 1 - i) / (n - i)
    one_or_more_i = 1 - not_i ** k
    not_better = (n - i) / n
    none_better = not_better ** k
    return one_or_more_i * none_better


def best_of_k(data, k, minimum=False):
    return sum(resample_probability(i, k, len(data)) * v
               for i, v in enumerate(sorted(data, reverse=minimum)))


def wilcoxon_signed_rank(d1, d2):
    non_zero_diff = [(x1 - y1) for x1, y1 in zip(d1, d2) if (x1 - y1) != 0]
    non_zero_diff.sort(key=abs)
    rank = 0
    pairs = len(non_zero_diff)
    total = 0
    while rank < pairs:
        identical = rank + 1
        signs = cmp(non_zero_diff[rank], 0)
        while (identical < pairs and
               abs(non_zero_diff[rank]) == abs(non_zero_diff[identical])):
            signs += cmp(non_zero_diff[identical], 0)
            identical += 1
        identical -= 1
        average_rank = (identical - rank) / 2.0 + rank + 1
        total += average_rank * signs
        rank = identical + 1
    std = math.sqrt((pairs * (pairs + 1) * (2 * pairs + 1)) / 6)
    try:
        if total > 0:
            use = -0.5
        else:
            use = 0.5
        z = (total + use) / std
    except ZeroDivisionError:
        z = 0
    return abs(total), pairs, std, z

linecycler = cycle(["-", "--", "-.", ":"])
