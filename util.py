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
    '''
    This chooses the proper way to open a file by examining its extension.
    Returns the function to use, either "open" or "gzip"
    '''
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


def bitcount(integer):
    '''
    Counts the number of set bits in an integer
    '''
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
    matplotlib.pyplot.figure(figsize=(5, 5))

# Generator used when plotting to cylce through the different line styles
linecycler = cycle(["-", "--", "-.", ":"])

# Dictionary converter from original name to name used in paper
pretty_name = {"normal": "Normal",
               "reorder": "Reorder",
               "dag": "DAG",
               "single": "Single",
               "skip": "Skip",
               "accumulate": "Accumulate"}

# Specifies what order lines should appear in graphs
line_order = {'normal': 1,
              'reorder': 2,
              'dag': 3,
              }
