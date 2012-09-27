PROBLEM=$1
NODES=$2
MUT=$3
SEED=$4

sed -e "s/PROBLEM/$PROBLEM/g" -e "s/NODES/$NODES/g" -e "s/MUT/$MUT/g" -e "s/SEED/$SEED/g" template.sub > temp.sub
qsub temp.sub
rm temp.sub
