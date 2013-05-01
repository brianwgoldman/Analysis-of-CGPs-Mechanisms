import sys
import json
from os import path
from collections import defaultdict
from util import find_median


def dict_of_lists():
    return defaultdict(list)

gather = defaultdict(dict_of_lists)
select = int(sys.argv[1])
whitelist = set()
with open(sys.argv[2], 'r') as f:
    for line in f.readlines():
        whitelist.add(tuple(json.loads(line)))

for filename in sys.argv[3:]:
    try:
        base = path.basename(filename)
        problem, duplicate, ordering, nodes, mut, seed = base.split('_')
        if len(whitelist) != 0:
            if (problem, duplicate, ordering, nodes, mut) not in whitelist:
                # Not in the white list, skip it
                continue
        with open(filename, 'r') as f:
            data = json.load(f)
        tuning = gather[problem, duplicate, ordering]
        tuning[nodes, mut].append(data[1]['evals'])
    except ValueError as e:
        print 'FAILED', filename, base.split('_')

for group_name, group_value in gather.items():
    most_runs = max(len(values) for values in group_value.itervalues())
    rankings = []

    for config, values in group_value.iteritems():
        while len(values) < most_runs:
            values.append(987654321)  # Arbitrary number for missing runs
        rankings.append((find_median(values), config))
    ordered = sorted(rankings)
    for number, (median, config) in enumerate(ordered):
        if number == select:
            break
        if 987654321 in group_value[config]:
            print >> sys.stderr, "FAILED", group_name + config
        print json.dumps(group_name + config)
