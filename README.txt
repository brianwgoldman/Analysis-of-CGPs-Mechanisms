cfg - Folder containing configuration files.
documentation - Folder containing files used to construct documentation.
output - Folder used to store tuning run output.  Raw data available upon request.
final - Folder used to store testing run output.  Raw data available upon request.

A built version of the documentation is available at: http://brianwgoldman.github.io/Analysis-of-CGPs-Mechanisms/
You can also check out the gh-pages branch of this repository.

The raw data for this project was too large to include, but is available on request.
Also see the rdata.csv file which contains most of the data for Table II
(evaluations to success).

To run experiments, use main.py
To see confidence intervals and other evaluations to success data, use interval.R.
To create bar plots, use bar_plot.py on "final" data.
To statistically compare data, use stats.py on "final" data.
To look at semantic behavior, use bit_behavior.py on "final" data.
To recreate the rdata.csv file from raw, use make_rdata.py on "final" data.
To create the never active plots, use never_actives.py on "final" data.
