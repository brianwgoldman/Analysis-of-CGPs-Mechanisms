for problem in encode decode multiply parity
do
	for ordering in normal reorder dag
	do
		for nodes in 50 100 200 500 1000 2000 5000 10000
		do
			echo ./runone.sh $problem single $ordering $nodes 1
			for duplicate in skip accumulate
			do
				for mut in 0.05 0.02 0.01 0.005 0.002 0.001 0.0005 0.0002
				do
					echo ./runone.sh $problem $duplicate $ordering $nodes $mut
				done
			done
		done
	done
done
