PROBLEM=$1
DUPLICATE=$2
ORDERING=$3
NODES=$4
MUT=$5
SUB=array.sub

sed -e "s/PROBLEM/$PROBLEM/g" -e "s/NODES/$NODES/g" -e "s/MUT/$MUT/g" -e "s/DUPLICATE/$DUPLICATE/g" -e "s/ORDERING/$ORDERING/g" $SUB > temp.sub
qsub -t 1-4 temp.sub
rm temp.sub
