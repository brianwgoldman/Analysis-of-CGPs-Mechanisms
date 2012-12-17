'''
Takes file names from the output/ folder and parses the information into
readable values and produces a graph.  Use this module as an executable to
process all information for a single problem, such as:

python plotter.py output/multiply*

Do not mix problems in a single run.  The graph will be saved to a .eps file
named after the problem used.

NOTE: You CANNOT use pypy for this as pylab is current unsupported.  Use
python 2.7 instead.
'''

from pylab import show, plot, legend, savefig, xlabel, ylabel, nan, gca, loglog
from scipy import stats
import math
import json
import sys
from os import path
from collections import defaultdict
from main import combine_results
from util import wilcoxon_signed_rank, linecycler

# Dictionary converter from original name to name used in paper
pretty_name = {"normal": "Normal",
               "reorder": "Reorder",
               "dag": "DAG", }

# Specifies what order lines should appear in graphs
order = {'normal': 1,
         'reorder': 2,
         'dag': 3,
         'mut': 4,
         }

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    raw = defaultdict(list)
    filecount = 0
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            problem, nodes, version, seed = base.split('_')
            seed = int(seed[:-4])
            with open(filename, 'r') as f:
                data = json.load(f)
            raw[problem, int(nodes), version].append(data['length_frequencies'])
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print 'Files Successfully Loaded', filecount

    #Find line information and best configurations
    lines = defaultdict(list)
    bests = defaultdict(list)
    for key, results in raw.iteritems():
        problem, nodes, version = key
        combined = [sum(group) for group in zip(*results)]
        mode = nan
        # Only gather data if median is less than the maximum
        if sum(combined) > 0:
            mode = max(range(len(combined)), key=combined.__getitem__)
            if len(combined) == 100:
                print version, len(combined), mode
            #mode = mode
            bests[version].append((mode, nodes, combined, results))
        lines[version].append((mode, nodes))

    # Plot the lines using the 'order' order
    for version, line in sorted(lines.iteritems(), key=lambda X: order[X[0]]):
        try:
            X, Y = zip(*sorted(line))
            #print version
            #for x, y in sorted(line):
            #    print x, y

        except ValueError:
            print version, line
            continue
        clean_x, clean_y = zip(*[(math.log(x), math.log(y)) for x, y in line
                                 if y is not nan])
        order, intercept = stats.linregress(clean_x, clean_y)[0:2]
        print stats.linregress(clean_x, clean_y)
        print version, order, math.exp(intercept)
        loglog(X, Y, label=pretty_name[version], linestyle=next(linecycler),
               linewidth=2.5)
    #ax = gca()
    #ax.set_yscale('log')
    legend(loc='best')
    ylabel("Number of Nodes")
    xlabel("Mode Number of Active Nodes")
    '''
    statify = {}
    print '\tBests'
    print 'version, nodes, (evals, deviation), active nodes'
    for version, experiments in bests.iteritems():
        score, label, combined, results = min(experiments)
        pretty = pretty_name[version]
        active = combined['phenotype'][0]
        print pretty, label, combined['evals'], active
        statify[version] = [result['evals'] for result in results]

    print "\nStatistical Tests"
    for version, data in statify.iteritems():
        print "%s with Normal" % pretty_name[version],
        print wilcoxon_signed_rank(statify['normal'], data)
        print stats.mannwhitneyu(statify['normal'], data)
    '''
    savefig(problem + ".eps", dpi=300)
    show()
