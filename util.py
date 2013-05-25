'''
Collection of utility functions with no other obvious home.
'''
from itertools import izip, cycle
from collections import defaultdict
import json
import os
import math
import gzip


def diff_count(data1, data2):
    '''
    Count the number of differences is two sets of data
    '''
    return sum(x != y for x, y in izip(data1, data2))


def open_file_method(filename):
    extension = filename.split('.')[-1]
    if extension == 'gz':
        return gzip.open
    return open


def load_configurations(filenames):
    '''
    Given a list of files containing json encoded dictionaries, combined
    the data into a single dictionary.  Will attempt to use file extension
    to detect correct file type.

    Parameters:

    - ``filenames``: The list of files paths.
    '''
    result = {}
    for filename in filenames:
        file_method = open_file_method(filename)
        with file_method(filename, 'r') as f:
            result.update(json.load(f))
    return result


def save_configuration(filename, data):
    '''
    Write a dictionary to the specified file in json format.  Will attempt to
    use file extension to detect correct file type.

    Parameters

    - ``filename``: The path to write to.
    - ``data``: The data to be written.
    '''
    file_method = open_file_method(filename)
    with file_method(filename, 'w') as f:
        json.dump(data, f)


def save_list(filename, data):
    '''
    Write a list of dictionaries to the file in a more human readable way.
    Will attempt to use file extension to detect correct file type.

    Parameters

    - ``filename``: The path to write to.
    - ``data``: The list of dictionaries to be written.
    '''
    file_method = open_file_method(filename)
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
    '''
    Returns the median of the data.
    '''
    ordered = sorted(data)

    length = len(data)
    middle = length // 2
    if length % 2 == 1:
        return ordered[middle]
    else:
        return (ordered[middle] + ordered[middle - 1]) / 2.0


def median_deviation(data, median=None):
    '''
    Returns the median and the median absolute deviation of the data.

    Parameters:

    - ``data``: The data to find the medians of.
    - ``median``: If the median is already known you can pass it in to save
      time.
    '''
    if median is None:
        median = find_median(data)
    return  median, find_median([abs(x - median) for x in data])


def resample_probability(i, k, n):
    '''
    Given ``k`` samples from ``n`` items, what is the probability that the
    ``ith`` best element in the original set is the best found in the sample.

    Parameters:

    - ``i``: The index being predicted.
    - ``k``: The sample size being drawn.
    - ``n``: The number of items being drawn from.
    '''
    n = float(n)
    not_i = (n - 1 - i) / (n - i)
    one_or_more_i = 1 - not_i ** k
    not_better = (n - i) / n
    none_better = not_better ** k
    return one_or_more_i * none_better


def best_of_k(data, k, minimum=False):
    '''
    Given a set of data, predict what the expected best result of drawing
    ``k`` samples from the same distribution.

    Parameters

    - ``data``: The set of data drawn from the distribution being analyzed.
    - ``k``: The number of samples to be drawn from the distribution.
    - ``minimum``: Specifies if you want the worst of k instead of the best.
    '''
    return sum(resample_probability(i, k, len(data)) * v
               for i, v in enumerate(sorted(data, reverse=minimum)))


def wilcoxon_signed_rank(d1, d2):
    '''
    Perform a statistical test paired data given in two data sets.  Returns
    W, the number of non-identical pairs, the standard deviation of the
    rankings, and finally the z value (which is only correct if the data
    contains more than 10 non identical pairs).
    '''
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


def entropy(data):
    unique = defaultdict(int)
    for d in data:
        unique[d] += 1
    total = float(len(data))
    return -sum((count / total) * math.log(count / total, 2)
                for count in unique.values())


def bitcount(integer):
    return bin(integer).count('1')


def set_fonts():
    '''
    Configures matplotlib to use only Type 1 fonts, and sets the figure size
    such that those fonts will be legible when the figure is inserted in
    a publication.
    '''
    import matplotlib
    matplotlib.rcParams['ps.useafm'] = True
    matplotlib.rcParams['pdf.use14corefonts'] = True
    matplotlib.rcParams['text.usetex'] = True
    matplotlib.pyplot.figure(figsize=(7, 5))

# Generator used when plotting to cylce through the different line styles
linecycler = cycle(["-", "--", "-.", ":"])

# Dictionary converter from original name to name used in paper
pretty_name = {"normal": "Normal",
               "reorder": "Reorder",
               "dag": "DAG", }

# Specifies what order lines should appear in graphs
line_order = {'normal': 1,
              'reorder': 2,
              'dag': 3,
              }
