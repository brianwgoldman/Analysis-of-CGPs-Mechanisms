'''
Takes file names from the final/ folder and parses the information into
readable values and produces statistical measures.  Use this module as an
executable to process all result information for a single problem, such as:

python stats.py final/multiply*.dat

Do not mix problems in a single run.

NOTE: You CANNOT use pypy for this as scipy is current unsupported.  Use
python 2.7 instead.
'''

import json
import sys
from os import path
from collections import defaultdict
from util import median_deviation, open_file_method
from scipy.stats.mstats import kruskalwallis, mannwhitneyu
from numpy.ma import masked_array


def make_rectangular(data, fill):
    width = len(max(data, key=len))
    return [masked_array(line + [fill] * (width - len(line)),
                         [False] * len(line) + [True] * (width - len(line)))
            for line in data]

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    statify = defaultdict(list)
    active = defaultdict(list)
    filecount = 0
    control_group = None
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            problem, dup, ordering, nodes, mut, seed = base.split('_')
            with open_file_method(filename)(filename, 'r') as f:
                data = json.load(f)
            version = dup, ordering, nodes, mut
            if (dup, ordering) == ('skip', 'normal'):
                control_group = version
            statify[version].append(data[1]['evals'])
            active[version].append(data[1]['phenotype'])
            filecount += 1
        except ValueError:
            print filename, "FAILED"

    # Kruskal's requires a rectangular matrix
    rect = make_rectangular(statify.values(), 10000001)

    print 'Files Successfully Loaded', filecount
    print 'Kruskal Wallis', kruskalwallis(rect)
    for version, data in statify.iteritems():
        print '--------- %s ---------' % str(version)
        print "MES, MAD", median_deviation(data)
        print 'Active', median_deviation(active[version])
        print 'Mann Whitney U against Control',
        print mannwhitneyu(statify[control_group], data)
