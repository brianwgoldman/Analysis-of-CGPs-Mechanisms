'''
Takes file names from the final/ folder and parses the information to
create the black and white graphs in Table III.  Use this module as an
executable to process all result information for a single problem, such as:

``python never_actives.py final/multiply_accumulate_normal_*.dat.gz``

Do not mix problems in a single run.

NOTE: You CANNOT use pypy for this as pylab is current unsupported.  Use
python 2.7 instead.
'''

import json
import sys
from os import path
from collections import defaultdict
from util import median_deviation, open_file_method, set_fonts
from pylab import show, get_cmap, concatenate, linspace, savefig
import pylab as plt
import matplotlib
import numpy as np


def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.
    cmap: colormap instance, eg. cm.jet. 
    N: number of colors.
    """

    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = concatenate((linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki],
                       colors_rgba[i, ki]) for i in xrange(N + 1)]
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N,
                                                     cdict, 1024)

if __name__ == '__main__':
    set_fonts()
    filecount = 0

    storage = []
    levels = set()
    outname = None
    percentages = []
    best_worst = 0
    # Run through all of the files gathering different seeds into lists
    for filename in sys.argv[1:]:
        base = path.basename(filename)
        try:
            print 'Processing file', filename
            outname = base.split('_')[:3]
            with open_file_method(filename)(filename, 'r') as f:
                data = json.load(f)
            graph_length = float(data[1]['bests'][-1]['graph_length'])
            percentages.append(data[1]['unused'] / graph_length)
            stripped = {}
            best_worst = max(best_worst, data[1]['bests'][0]['fitness'])
            for best in data[1]['bests']:
                stripped[best['fitness']] = map(int, best['never_active'])
                levels.add(best['fitness'])
            storage.append(stripped)
            filecount += 1
        except ValueError:
            print filename, "FAILED"
    print "Loaded", filecount
    print "Median final never active", median_deviation(percentages)

    # Limits the number of unique fitness levels to plot
    ysteps = 40
    scan_lines = [x for x in sorted(levels) if x >= best_worst]
    if len(scan_lines) > ysteps:
        step = float(len(scan_lines)) / ysteps
        print 'Step', step, 'highest', int(step * (ysteps - 1)), len(scan_lines)
        scan_lines = [scan_lines[int(x * step)] for x in range(ysteps)]
        # Ensure that the maximum fitness is always added to the scan lines
        if scan_lines[-1] != max(levels):
            scan_lines.append(max(levels))
    combined = defaultdict(list)
    for stored in storage:
        index = 0
        fitnesses, values = zip(*sorted(stored.items()))
        # Finds the update closest to the scan line without going over
        for scan_line in scan_lines:
            while index < len(fitnesses) and fitnesses[index] <= scan_line:
                index += 1
            index -= 1
            if index >= 0 and fitnesses[index] <= scan_line:
                combined[scan_line].append(values[index])
            else:
                index = 0

    for level, data in sorted(combined.items()):
        print len(data), 'runs reached fitness', level
    # Create the heatmap matrix
    Z = []
    complete_levels = []
    groups = 50
    genome_size = None
    for level, partial in sorted(combined.items()):
        # Only plots complete levels
        if len(partial) == filecount:
            # Convert the number to a percentage
            each = [sum(joint) / float(len(joint)) * 100
                    for joint in zip(*partial)]
            genome_size = len(each)
            size = len(each) / groups
            grouped = [each[i * size:(i + 1) * size]
                       for i in range(groups + 1)]
            merged = [sum(group) / float(len(group)) for group in grouped
                      if len(group) > 0]
            Z.append(merged)
            complete_levels.append(level)
    print 'Fitness levels reached by all runs:', len(complete_levels)
    Z = np.array(Z).transpose()
    X, Y = np.meshgrid(range(0, genome_size + 1, genome_size / groups), complete_levels)
    im = plt.pcolormesh(X, Y, Z.transpose(), cmap=cmap_discretize("binary", 5), vmin=0, vmax=100)
    cbar = plt.colorbar(im, orientation='horizontal')
    cbar.set_label("Percentage Of Runs Where Node Was Never Active")
    plt.ylim(min(complete_levels), max(complete_levels))
    plt.xlabel('Node Index')
    plt.ylabel('Fitness Level')
    savefig('_'.join(outname) + '.eps', dpi=300)
    plt.show()
