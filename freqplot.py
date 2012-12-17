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
               "reorder": "Reorder",
               "dag": "DAG", }

# Specifies what order lines should appear in graphs
order = {'normal': 1,
         'reorder': 2,
         'dag': 3,
         }

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    '''
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
    '''

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
    lines = {}
    bests = defaultdict(list)
    for key, results in raw.iteritems():
        problem, nodes, version = key
        combined = [sum(group) for group in zip(*results)]
        mode = nan
        # Only gather data if median is less than the maximum
        try:
            total = float(sum(combined))
            lines[version] = [count / total for count in combined]
        except ZeroDivisionError:
            pass
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
        mode_index, highest_non_zero = 0, 0
        total_index, total = 0, 0
        lower, upper = 0, 0
        for index, datum in enumerate(line):
            if datum > line[mode_index]:
                mode_index = index
            if datum != 0:
                highest_non_zero = index
            if total < 0.9999:
                total += datum
                if lower == 0 and total > 0.025:
                    lower = index
                if upper == 0 and total > 0.975:
                    upper = index
                if total >= 0.9999:
                    total_index = index
        print version, mode_index, lower, upper, total_index, highest_non_zero
        plot(line, label=pretty_name[version], linestyle=next(linecycler),
               linewidth=2.5)
    #ax = gca()
    #ax.set_yscale('log')
    legend(loc='best')
    xlabel("Number of Active Nodes")
    ylabel("Frequency of Evolution Individual")
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
    savefig("length_frequencies.eps", dpi=300)
    show()
