#!/usr/bin/Rscript
# This script parses through the "rdata.csv" data file and creates the confidence
# interval information displayed in Table II.
library(boot)

all_data <- read.csv("rdata.csv", header=TRUE)

median.fun <- function(x, d) {
  # Used in boot strapping
  return(median(x[d]))
}

straper <- function(data_in) {
  # Find the bootstrapped confidence interval
  bootobj <- boot(data=data_in, statistic=median.fun, R = 100)
  result <- boot.ci(bootobj, type = "norm")$normal
  return(c(lower.ci=result[2], median=median(data_in), upper.ci=result[3]))
}

# Aggregates the information across each problem and configuration variant
result <- aggregate(evaluations~problem+duplication+ordering+genome_size+mutation_rate, data=all_data, FUN=straper)
options(width=200)
# Displays the data ordered by the problem and then the median number of evaluations
result[with(result, order(problem, evaluations[,2])),]

