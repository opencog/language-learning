#!/bin/bash

declare -a windows=(1 3)
declare -a alphas=(0.5 0.7 0.9 1.1 1.3 1.5)
workers=8
dim=300
epochs=1000000
min_freq=5

for window in "${windows[@]}"
do
	for alpha in "${alphas[@]}"
	do
		append=WO${workers}D${dim}E${epochs}M${min_freq}A${alpha}W${window}
		~/.julia/v0.4/AdaGram/train.sh $1 $2                           	\
		adagram_${1}_${append} 	--workers=$workers --alpha=$alpha 		\
		--dim=$dim --epochs=$epochs --window=$window --min-freq=$min_freq
	done
done
