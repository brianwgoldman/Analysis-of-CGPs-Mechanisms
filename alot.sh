MUT=$1
START=$2
END=$3

for SEED in `seq $START $END`
do
	./runone.sh quartic 100 $MUT $SEED
	./runone.sh parity 3000 $MUT $SEED
	./runone.sh multiply 3000 $MUT $SEED
done
