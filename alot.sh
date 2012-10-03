PROBLEMS='multiply paige parity quartic'
NODES=$1
MUT=$2
START=$3
END=$4

for SEED in `seq $START $END`
do
	for PROBLEM in $PROBLEMS
	do
		./runone.sh $PROBLEM $NODES $MUT $SEED
	done
done
