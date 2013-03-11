import sys
from subprocess import call
from os import path
import json


def base_generator(low, high):
    for problem in ['encode', 'decode', 'multiply', 'parity']:
        for ordering in ['normal', 'reorder', 'dag']:
            for nodes in [50, 100, 200, 500, 1000, 2000, 5000, 10000]:
                for seed in range(low, high + 1):
                    yield [problem, 'single', ordering, nodes, 1, seed]
                for duplicate in ['skip', 'accumulate']:
                    for mut in [0.05, 0.02, 0.01, 0.005,
                                0.002, 0.001, 0.0005, 0.0002]:
                        for seed in range(low, high + 1):
                            yield [problem, duplicate, ordering,
                                   nodes, mut, seed]


def next_level(low, high, filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            config = json.loads(line)
            for seed in range(low, high + 1):
                yield config + [seed]

low = int(sys.argv[1])
high = int(sys.argv[2])
to_add = 256 - int(sys.argv[3])

if len(sys.argv) <= 4:
    generator = base_generator(low, high)
else:
    generator = next_level(low, high, sys.argv[4])

added = 0
try:
    with open('complete.txt', 'r') as f:
        complete = int(f.read())
except (ValueError, IOError):
    complete = 0
print 'Complete', complete, 'Adding', to_add

for index, config in enumerate(generator):
    if index >= complete:
        arguments = map(str, config)
        # if output file already exists, skip it
        file_would_be = path.join('output', '_'.join(arguments) + '.dat')
        if not path.exists(file_would_be):
            print arguments
            if call(['./runone.sh'] + arguments):
                print "NON ZERO!"
            added += 1
        if added >= to_add:
            break

with open('complete.txt', 'w') as f:
    f.write(str(index + 1) + '\n')
print index + 1
