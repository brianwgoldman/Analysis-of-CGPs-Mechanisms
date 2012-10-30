START=$1
END=$2

for SEED in `seq $START $END`
do
	./runone.sh parity 3000 0.1 $SEED onemut.sub
	./runone.sh multiply 3000 0.1 $SEED onemut.sub
	./runone.sh mux 3000 0.1 $SEED onemut.sub
	./runone.sh demux 3000 0.1 $SEED onemut.sub
	for MUT in 0.0001 0.0002 0.0004 0.0008 0.001 0.002 0.004 0.008 0.01 0.02 0.04 0.08 0.1 0.2 0.4 0.8
	do
		for SUB in mutate.sub reeval.sub
		do
			./runone.sh parity 3000 $MUT $SEED $SUB
			./runone.sh multiply 3000 $MUT $SEED $SUB
			./runone.sh mux 3000 $MUT $SEED $SUB
			./runone.sh demux 3000 $MUT $SEED $SUB
		done
	done
done
