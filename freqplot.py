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
import json
import sys
from os import path
from collections import defaultdict
from main import combine_results
from util import wilcoxon_signed_rank, linecycler

# Dictionary converter from original name to name used in paper
pretty_name = {"normal": "Normal",
               "single": "Single",
               "skip": "Skip",
               "accumulate": "Accumulate"}

# Specifies what order lines should appear in graphs
order = {'normal': 1,
         'reorder': 2,
         'dag': 3,
         }

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    lines = {}
    filecount = 0
    key = sys.argv[1]
    for filename in sys.argv[2:]:
        base = path.basename(filename)
        try:
            version = base[:-4]
            with open(filename, 'r') as f:
                data = json.load(f)
            lines[version] = data[key]
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print 'Files Successfully Loaded', filecount

    # Plot the lines using the 'order' order
    for version, line in sorted(lines.iteritems(), key=lambda X: order[X[0]]):
        '''
        try:
            X, Y = zip(*sorted(line))
            print version
            for x, y in sorted(line):
                print x, y

        except ValueError:
            print version, line
            continue
        '''
        plot(line, label=version, linestyle=next(linecycler),
               linewidth=2.5)
    #ax = gca()
    #ax.set_yscale('log')
    legend(loc='best')
    xlabel("Number of Nodes")
    ylabel("Median Evaluations until Success")
    '''
    statify = {}
    print '\tBests'
    print 'version, mutation rate, (evals, deviation),',
    print 'genes not including output'
    for version, data in bests.iteritems():
        score, rate, combined, results = min(datum for datum
                                             in data if datum[0] is not nan)
        pretty = pretty_name[version]
        genes = combined['phenotype'][0] * 3
        if version != 'normal':
            print pretty, rate, combined['evals'], genes
            statify[version] = [result['evals'] for result in results]
        else:
            print pretty, rate, combined['normal'], genes
            statify['normal'] = [result['normal'] for result in results]

    print "\nStatistical Tests"
    for version, data in statify.iteritems():
        print "%s with Normal" % pretty_name[version],
        print wilcoxon_signed_rank(statify['normal'], data)
    '''
    savefig(key + ".eps", dpi=300)
    show()
