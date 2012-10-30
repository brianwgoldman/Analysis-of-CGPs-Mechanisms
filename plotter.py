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

from pylab import show, loglog, legend, savefig, xlabel, ylabel, nan
import json
import sys
from os import path
from collections import defaultdict
from main import combine_results
from util import wilcoxon_signed_rank, linecycler

# Dictionary converter from original name to name used in paper
pretty_name = {"normal": "Normal",
               "onemut": "Single",
               "reeval": "Skip",
               "mutate": "Accumulate"}

# Specifies what order lines should appear in graphs
order = {'normal': 1,
         'reeval': 2,
         'mutate': 3,
         'onemut': 4}

# Run through all of the files gathering different seeds into lists
groupings = defaultdict(list)
filecount = 0
for filename in sys.argv[1:]:
    base = path.basename(filename)
    try:
        problem, nodes, rate, version, _ = base.split('_')
        with open(filename, 'r') as f:
            data = json.load(f)
        groupings[problem, int(nodes), float(rate), version].append(data[1])
        filecount += 1
    except ValueError:
        print filename, "FAILED"
print 'Files Successfully Loaded', filecount

# From each collected experiment find line information and best configurations
lines = defaultdict(list)
rates = set()
bests = defaultdict(list)
for key, results in groupings.iteritems():
    problem, nodes, rate, version = key
    if version != 'onemut':
        rates.add(rate)
    combined = combine_results(results)
    toplot = nan
    normal = nan
    # Only gather data if median is less than the maximum
    if combined['evals'][0] < 10000000:
        toplot = combined['evals'][0]
        if combined['normal'][0] < 10000000:
            normal = combined['normal'][0]
    lines[version].append((rate, toplot))
    # Only include in bests if fully successful
    if combined['success'][0] == 1:
        bests[version].append((toplot, rate, combined, results))
    if version == 'reeval':
        lines['normal'].append((rate, normal))
        # Ensure that normal was fully successful
        if max([result['normal'] for result in results]) < 10000000:
            bests['normal'].append((normal, rate, combined, results))
# Since we only have 1 data point for Single, expand it across all rates used
try:
    lines['onemut'] = [(rate, lines['onemut'][0][1]) for rate in sorted(rates)]
except IndexError:
    pass

# Plot the lines using the 'order' order
for version, line in sorted(lines.iteritems(), key=lambda X: order[X[0]]):
    try:
        X, Y = zip(*sorted(line))
    except ValueError:
        print version, line
        continue
    loglog(X, Y, label=pretty_name[version], linestyle=next(linecycler),
           linewidth=2.5)

legend(loc='best')
xlabel("Mutation Rate")
ylabel("Median Evaluations until Success")
statify = {}
print '\tBests'
print 'version, mutation rate, (evals, deviation), genes not including output'
for version, data in bests.iteritems():
    score, rate, combined, results = min(datum for datum
                                         in data if datum[0] is not nan)
    pretty = pretty_name[version]
    if version != 'normal':
        print pretty, rate, combined['evals'], combined['phenotype'][0] * 3
        statify[version] = [result['evals'] for result in results]
    else:
        print pretty, rate, combined['normal'], combined['phenotype'][0] * 3
        statify['normal'] = [result['normal'] for result in results]

print "\nStatistical Tests"
for version, data in statify.iteritems():
    print "%s with Normal" % pretty_name[version],
    print wilcoxon_signed_rank(statify['normal'], data)
savefig(problem + ".eps", dpi=300)
show()
