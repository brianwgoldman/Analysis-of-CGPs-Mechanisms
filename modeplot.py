'''
Takes file names from the output/ folder and parses the information into
readable values and produces a graph.  Use this module as an executable to
process all mode active length frequency information into growth rates.

python modeplot.py output/neutral_*

Do not mix problems in a single run.  The graph will be saved to a .eps file
named after the problem used.

NOTE: You CANNOT use pypy for this as pylab is current unsupported.  Use
python 2.7 instead.
'''

from pylab import show, legend, savefig, xlabel, ylabel, nan, loglog
from scipy import stats
import math
import json
import sys
from os import path
from collections import defaultdict
from util import linecycler, pretty_name, line_order, set_fonts

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
            raw[problem, int(nodes), version].append(data)
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print 'Files Successfully Loaded', filecount

    set_fonts()
    # Find line information and best configurations
    lines = defaultdict(list)
    for key, results in raw.iteritems():
        problem, nodes, version = key
        combined = [sum(group) for group in zip(*results)]
        mode = nan
        # Only gather data if something was actually recorded
        if sum(combined) > 0:
            # Neat python trick to find the mode
            mode = max(range(len(combined)), key=combined.__getitem__)
        lines[version].append((mode, nodes))

    print 'Version, order, scalar'
    # Plot the lines using the 'line_order' order
    for version, line in sorted(lines.iteritems(),
                                key=lambda X: line_order[X[0]]):
        try:
            X, Y = zip(*sorted(line))
        except ValueError:
            print 'Error in', version, line
            continue
        # Preprocess the line to put it in a form linregress can solve
        clean_x, clean_y = zip(*[(math.log(x), math.log(y)) for x, y in line
                                 if y is not nan])
        order, intercept = stats.linregress(clean_x, clean_y)[0:2]
        print version, order, math.exp(intercept)
        loglog(X, Y, label=pretty_name[version], linestyle=next(linecycler),
               linewidth=2.5)
    legend(loc='best')
    ylabel("Number of Nodes")
    xlabel("Mode Number of Active Nodes")
    savefig(problem + ".eps", dpi=300)
    show()
