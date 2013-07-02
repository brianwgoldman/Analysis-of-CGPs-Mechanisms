'''
Parses through any number of output files and reports the number of evaluations
and runs performed.

pypy counter.py output/* scale/* final/*

'''

import json
import sys
from os import path
from collections import defaultdict
from util import open_file_method


if __name__ == '__main__':
    runs = defaultdict(int)
    evals = defaultdict(int)
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            problem = base.split('_')[0]
            with open_file_method(filename)(filename, 'r') as f:
                data = json.load(f)
            print filename, data[1]['evals']
            evals[problem] += data[1]['evals']
            runs[problem] += 1
        except ValueError:
            print filename, "FAILED"

    print 'Problem\tRuns\tEvals'
    for problem in runs.keys():
        print problem, runs[problem], evals[problem]
    print '--------------'
    print 'Total', sum(runs.values()), sum(evals.values())
