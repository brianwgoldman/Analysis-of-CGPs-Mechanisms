PROBLEM=$1
NODES=$2
MUT=$3
START=$4
END=$5

for SEED in `seq $START $END`
do
	./runone.sh $PROBLEM $NODES $MUT $SEED
done
