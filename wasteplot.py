from pylab import plot, show, loglog, legend, savefig, xlabel, ylabel, gca
from itertools import cycle
lines = ["-", "--", "-.", ":"]
linecycler = cycle(lines)

X = range(1, 3000)
for m in [0.0001, 0.0002, 0.0004, 0.008, 0.001, 0.002, 0.004, 0.008, 0.01, 0.02, 0.04, 0.08, 0.1, 0.2, 0.4, 0.8]:
    Y = [(1 - m) ** (x * 3 + 1) for x in X]
    #Y = [m * (x * 3 + 1) * (1 - m) ** (x * 3 + 1 - 1) for x in X]
    plot(X, Y, label=str(m), linestyle=next(linecycler), linewidth=2.5)
#ax = gca()
#ax.set_xscale('log')
legend(loc='upper right')
from pylab import xlim
xlim(1, 500)
#xlabel("Mutation Rate")
#ylabel("Mean Evaluations until Success")
xlabel("Number of Active Nodes")
ylabel("Probability of No Active Node Mutating")

#savefig(problem + ".eps", dpi=300)
savefig("Probability.eps", dpi=300)
show()
