#!/bin/bash

declare -a windows=(1 3)
declare -a alphas=(0.1 0.3 0.5 0.7 0.9 1.1)
workers=8
dim=300
epochs=1

for window in "${windows[@]}"
do
	for alpha in "${alphas[@]}"
	do
		append=WO${workers}D${dim}E${epochs}A${alpha}W${window}
		~/.julia/v0.4/AdaGram/train.sh $1 $2                           	\
		adagram_${1}_${append} 	--workers=$workers --alpha=$alpha 		\
		--dim=$dim --epochs=$epochs --window=$window 
	done
done
