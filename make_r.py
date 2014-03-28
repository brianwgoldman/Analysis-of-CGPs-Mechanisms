'''
This will parse through all files in the final folder and produce
R parsable output for use in analysis.  Run as a stand alone
executable in the form of:

python make_r.py final/*.dat.gz > rdata.csv
'''
from __future__ import print_function
import sys
from os import path
import json
from util import open_file_method

column_headers = ['problem', 'duplication', 'ordering', 'genome_size',
                  'mutation_rate', 'seed', 'evaluations']
print(','.join(column_headers))

# Loop through all command line arguments
for filename in sys.argv[1:]:
    base = path.basename(filename)
    try:
        problem, dup, ordering, nodes, mut, seed = base.split('_')
        with open_file_method(filename)(filename, 'r') as f:
            data = json.load(f)
        seed = seed.split('.')[0]
        line = ','.join([problem, dup, ordering, nodes,
                         mut, seed, str(data[1]['evals'])])
        print(line)

    except ValueError:
        print("FAILED", filename)
