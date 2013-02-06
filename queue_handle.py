import sys
from subprocess import call
from os import path


def generator():
    for problem in ['encode', 'decode', 'multiply', 'parity']:
        for ordering in ['normal', 'reorder', 'dag']:
            for nodes in [50, 100, 200, 500, 1000, 2000, 5000, 10000]:
                yield problem, 'single', ordering, nodes, 1
                for duplicate in ['skip', 'accumulate']:
                    for mut in [0.05, 0.02, 0.01, 0.005,
                                0.002, 0.001, 0.0005, 0.0002]:
                        yield problem, duplicate, ordering, nodes, mut

seed = sys.argv[1]
to_add = 256 - int(sys.argv[2])
added = 0
try:
    with open('complete.txt', 'r') as f:
        complete = int(f.read())
except (ValueError, IOError):
    complete = 0
print 'Complete', complete, 'Adding', to_add

for index, config in enumerate(generator()):
    if index >= complete:
        arguments = map(str, config) + [seed]
        # if output file already exists, skip it
        file_would_be = path.join('output', '_'.join(arguments) + '.dat')
        if not path.exists(file_would_be):
            if call(['./runone.sh'] + arguments):
                print "NON ZERO!"
            added += 1
        if added >= to_add:
            break

with open('complete.txt', 'w') as f:
    f.write(str(index + 1) + '\n')
print index + 1
