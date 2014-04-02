'''
Takes file names from the final/ folder as command line arguments
and parses the semantic information to produce the contents of Table VI.
Use this module as an executable to process each problem's results:

``python bit_behavior final/decode_*.dat.gz``

Note: Do not mix results from different problems.
'''

import json
import sys
from os import path
from collections import defaultdict
from util import find_median, open_file_method, pretty_name



if __name__ == '__main__':
    filecount = 0
    # which statistics to pull out of the files
    interesting = [
     'active_nodes_changed',  # How many nodes that were active before and after the mutation changed behavior at least 1 bit
     'reactivated_nodes',  # How many nodes did active -> inactive -> active
     'inactive_bits_changed',  # For nodes that were active -> inactive -> active, how many bits changed in the process
    ]

    # Collect information from the files
    combined = defaultdict(lambda: defaultdict(list))
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            print 'Processing file', filename
            with open_file_method(filename)(filename, 'r') as f:
                data = json.load(f)
            # Converts the filename into a key
            version = tuple(base.split('_')[1:3])
            # extract each statistic
            for test in interesting:
                result = data[1][test]
                try:
                    percentage = result['0'] / float(sum(result.values()))
                except KeyError:
                    percentage = 0
                # Inverts to become inactive_bits_unchnaged
                if test == 'inactive_bits_changed':
                    percentage = 1 - percentage
                combined[version][test].append(percentage * 100)
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print "Loaded", filecount
    # Finds the median results for each of the statistics
    for version, table in combined.items():
        for test, line in sorted(table.items()):
            combined[version][test] = find_median(line)
    # print the information in sorted order based on the first key
    for version in sorted(combined.keys(), key=lambda version: combined[version][interesting[0]]):
        duplicate, ordering = version
        duplicate = ('\emph{%s}' % pretty_name[duplicate]).rjust(18)
        ordering = ('\emph{%s}' % pretty_name[ordering]).rjust(14)
        # LaTeX formatting
        print ' & '.join([duplicate, ordering] + ["{0:.2f}\%".format(combined[version][test])
                                                  for test in interesting]) + ' \\\\ \hline'
