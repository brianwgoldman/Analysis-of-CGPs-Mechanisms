#!/bin/bash
PROBLEM=$1
DUPLICATE=$2
ORDERING=$3
NODES=$4
MUT=$5
SEED=$6
SUB=sub.sub

sed -e "s/PROBLEM/$PROBLEM/g" -e "s/NODES/$NODES/g" -e "s/MUT/$MUT/g" -e "s/DUPLICATE/$DUPLICATE/g" -e "s/ORDERING/$ORDERING/g"\
    -e "s/SEED/$SEED/g" $SUB > temp.sub
qsub temp.sub
rm temp.sub
