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

for key, results in sorted(groupings.items()):
    problem, nodes, rate, version = key
    combined = combine_results(results)
    fitness = combined['fitness']
    if version in ['normal', 'reeval']:
        print problem, version, combined['evals']
    if version == 'normal':
        lost = (1 - (1 - rate) ** combined['phenotype'][0])
        print problem, 'expected', combined['evals'] * lost
