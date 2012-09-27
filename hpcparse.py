import json
import sys
from collections import defaultdict
from main import combine_results


groupings = defaultdict(list)
for filename in sys.argv[1:]:
    problem, nodes, rate, version, _ = filename.split('_')
    with open(filename, 'r') as f:
        data = json.load(f)
    groupings[problem, nodes, rate, version].append(data[1])

for key, results in groupings.iteritems():
    print key, combine_results(results)
