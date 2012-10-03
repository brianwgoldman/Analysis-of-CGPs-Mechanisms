import json
import sys
from os import path
from collections import defaultdict
from main import combine_results


groupings = defaultdict(list)
for filename in sys.argv[1:]:
    base = path.basename(filename)
    problem, nodes, rate, version, _ = base.split('_')
    with open(filename, 'r') as f:
        data = json.load(f)
    groupings[problem, int(nodes), float(rate), version].append(data[1])

bests = defaultdict(tuple)
for key, results in groupings.iteritems():
    problem, nodes, rate, version = key
    combined = combine_results(results)
    fitness = combined['fitness']
    bests[problem, version] = max(bests[problem, version],
                                  (fitness, nodes, rate))

for best in sorted(bests.items()):
    print best
