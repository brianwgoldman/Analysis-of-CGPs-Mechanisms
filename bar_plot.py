'''
Takes file names from the final/ folder and parses the information to
create the bar charts in Table IV.  Use this module as an
executable to process all result information for a single problem, such as:

python bar_plot.py final/multiply_accumulate_normal_*.dat.gz

Do not mix problems in a single run.

NOTE: You CANNOT use pypy for this as pylab is current unsupported.  Use
python 2.7 instead.
'''

import json
import sys
from os import path
from collections import defaultdict
from util import open_file_method, set_fonts
from evolution import Individual
from pylab import show, savefig
import pylab as plt
from numpy import zeros


if __name__ == '__main__':

    set_fonts()
    filecount = 0

    behavior = defaultdict(lambda: zeros(2))

    outname = None
    # Run through all of the files gathering different seeds into lists
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            print 'Processing file', filename
            # Load the file
            with open_file_method(filename)(filename, 'r') as f:
                data = json.load(f)
            # Extract details about the configuration from the file's name
            outname = base.split('_')[:3]
            best = data[1]['bests'][-1]
            test = data[1]['test_inputs']

            # Semantics of always true / always false
            constants = {0, 2 ** len(test) - 1}

            # Reconstruct the best individual found in this run
            individual = Individual.reconstruct_individual(best, test)
            simplified = individual.new(Individual.simplify)

            active_indices = set(individual.active)
            used_indices = set(simplified.active)

            # Find the set of semantics used in the simplified individual
            useful_semantics = {simplified.semantics[node_index]
                                for node_index in simplified.active
                                if simplified.semantics[node_index]
                                not in constants}
            # Find the set of semantics in the active individual.  Superset of useful.
            active_semantics = {individual.semantics[node_index] for node_index
                                in individual.active}
            # Look at each nodes semantics
            for node_index in range(individual.graph_length):
                if individual.never_active[node_index]:
                    continue
                semantic = individual.semantics[node_index]
                activity = int(node_index not in active_indices)
                key = None
                # Determine what kind of node this is
                if semantic in constants:
                    key = 'Constant'
                elif semantic in useful_semantics:
                    if node_index in used_indices:
                        key = 'Used'
                    else:
                        key = 'Useful'
                elif semantic in active_semantics:
                    key = 'Intron'
                else:
                    key = 'Explore'
                behavior[key][activity] += 1
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print "Loaded", filecount

    # Plotting tools
    one = ('Used', 'Explore')
    both = ('Useful', 'Intron', 'Constant')
    width = 0.2
    results = []
    bar_type = 0
    colors = ['m', 'y', 'c', 'g', 'b', 'r']
    hatches = patterns = ('\\', '//', '\\\\', '/', 'x',
                          '.', '-', '+', '*', 'o', 'O')
    names = []
    total = float(filecount)
    for index, key in enumerate(one):
        results.append(plt.bar(index, max(behavior[key]) / total, width,
                               color=colors[len(names) % len(colors)],
                               hatch=hatches[len(names) % len(hatches)]))
        names.append(key)
    for index, key in enumerate(both):
        offset = width * (index + 1)
        locs = [offset, offset + 1]
        results.append(plt.bar(locs, behavior[key] / total, width,
                               color=colors[len(names) % len(colors)],
                               hatch=hatches[len(names) % len(hatches)]))
        names.append(key)
    plt.ylabel('Average Number Of Nodes')
    plt.xticks([0.4, 1.4], ['Active', 'Inactive'])
    plt.legend(zip(*results)[0], names, loc='best')
    savefig('bar_' + '_'.join(outname) + '.eps', dpi=300)
    show()
