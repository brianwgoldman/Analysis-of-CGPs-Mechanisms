from pylab import plot, show, loglog, legend, savefig, xlabel, ylabel, gca
import json
import sys
from os import path
from collections import defaultdict
from main import combine_results
from itertools import cycle
lines = ["-", "--", "-.", ":"]
linecycler = cycle(lines)

pretty_name = {"normal": "Normal",
               "onemut": "Single",
               "reeval": "Skip",
               "mutate": "Accumulate"}

order = {'normal': 1,
         'reeval': 2,
         'mutate': 3,
         'onemut': 4}

groupings = defaultdict(list)
for filename in sys.argv[1:]:
    base = path.basename(filename)
    try:
        problem, nodes, rate, version, _ = base.split('_')
        with open(filename, 'r') as f:
            data = json.load(f)
        groupings[problem, int(nodes), float(rate), version].append(data[1])
    except ValueError:
        print filename, "FAILED"
lines = defaultdict(list)
rates = set()
for key, results in groupings.iteritems():
    problem, nodes, rate, version = key
    if version != 'onemut':
        rates.add(rate)
    combined = combine_results(results)
    if combined['success'][0] == 1:
        lines[version].append((rate, float(combined['evals'][0])))
        if version == 'reeval':
            if max([result['normal'] for result in results]) < 10000000:
                lines['normal'].append((rate, combined['normal'][0]))
try:
    lines['onemut'] = [(rate, lines['onemut'][0][1]) for rate in sorted(rates)]
except IndexError:
    pass

for version, line in sorted(lines.iteritems(), key=lambda X: order[X[0]]):
    try:
        X, Y = zip(*sorted(line))
    except ValueError:
        print version, line
        continue
    print version, X, Y
    loglog(X, Y, label=pretty_name[version], linestyle=next(linecycler),
           linewidth=2.5)
#ax = gca()
#ax.set_yscale('log')
legend(loc='best')
xlabel("Mutation Rate")
ylabel("Mean Evaluations until Success")

savefig(problem + ".eps", dpi=300)
show()
