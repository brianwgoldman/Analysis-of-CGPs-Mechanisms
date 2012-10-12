START=$1
END=$2

for SEED in `seq $START $END`
do
	./runone.sh quartic 100 0.1 $SEED onemut.sub
	./runone.sh parity 3000 0.1 $SEED onemut.sub
	./runone.sh multiply 3000 0.1 $SEED onemut.sub
	for MUT in 0.001 0.002 0.004 0.008 0.01 0.02 0.04 0.08 0.1
	do
		for SUB in mutate.sub reeval.sub
		do
			./runone.sh quartic 100 $MUT $SEED $SUB
			./runone.sh parity 3000 $MUT $SEED $SUB
			./runone.sh multiply 3000 $MUT $SEED $SUB
		done
	done
done
