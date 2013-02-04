'''
Takes file names from the output/ folder and parses the information into
readable values and produces a graph.  Use this module as an executable to
process all length frequency information for a single problem, such as:

python freqplot.py output/neutral_100_*.frq

Do not mix problems or problem sizes in a single run.
The graph will be saved to a .eps file named after the problem size used.

NOTE: You CANNOT use pypy for this as pylab is current unsupported.  Use
python 2.7 instead.
'''

from pylab import show, plot, legend, savefig, xlabel, ylabel
import json
import sys
from os import path
from collections import defaultdict
from util import linecycler, pretty_name, line_order

if __name__ == '__main__':
    # Run through all of the files gathering different seeds into lists
    raw = defaultdict(list)
    filecount = 0
    name = ''
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            problem, nodes, version, seed = base.split('_')
            name = nodes
            seed = int(seed[:-4])
            with open(filename, 'r') as f:
                data = json.load(f)
            raw[problem, int(nodes), version].append(data)
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print 'Files Successfully Loaded', filecount

    # Find line information and best configurations
    lines = {}
    bests = defaultdict(list)
    for key, results in raw.iteritems():
        problem, nodes, version = key
        # Total across all seeds for each length
        combined = [sum(group) for group in zip(*results)]
        # Ignore if absolutely no information was recorded
        try:
            total = float(sum(combined))
            lines[version] = [count / total for count in combined]
        except ZeroDivisionError:
            pass
    print "Version, Mode, [lower, upper], <99.99%, Highest"
    # Plot the lines using the 'line_order' order
    for version, line in sorted(lines.iteritems(),
                                key=lambda X: line_order[X[0]]):
        mode_index, highest_non_zero = 0, 0
        total_index, total = 0, 0
        lower, upper = 0, 0
        # Look through the line for empirical information
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
        bound = "[%i, %i]" % (lower, upper)
        # Display empirical information
        print version, mode_index, bound, total_index, highest_non_zero
        plot(line, label=pretty_name[version], linestyle=next(linecycler),
               linewidth=2.5)
    legend(loc='best')
    xlabel("Number of Active Nodes")
    ylabel("Frequency of Evolved Individual")
    savefig("length_frequencies_%s.eps" % name, dpi=300)
    show()
