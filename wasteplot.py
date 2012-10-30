from pylab import plot, show, legend, savefig, xlabel, ylabel
from util import linecycler

X = range(1, 1000)
for m in [0.0001, 0.0002, 0.0004, 0.008, 0.001, 0.002, 0.004,
          0.008, 0.01, 0.02, 0.04, 0.08, 0.1, 0.2, 0.4, 0.8]:
    Y = [(1 - m) ** x for x in X]
    plot(X, Y, label=str(m), linestyle=next(linecycler), linewidth=2.5)
legend(loc='best', title='Mutation Rate')
xlabel("Number of Active Genes")
ylabel("Probability of No Active Gene Mutating")

savefig("Probability.eps", dpi=300)
show()
