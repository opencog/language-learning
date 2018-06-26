#!/bin/bash

# This file lets do sequential training of an AdaGram model with a range
# of parameters.
# Usage: ./train_multiple_adagram <corpus> <dictionary>
# ASuMa, May 2018


declare -a windows=(5)
declare -a alphas=(0.9 1.1 1.3)
workers=8
dim=300
epochs=1000000
min_freq=4
remove_top_k=2

for window in "${windows[@]}"
do
	for alpha in "${alphas[@]}"
	do
		append=WO${workers}D${dim}E${epochs}M${min_freq}A${alpha}W${window}R${remove_top_k}
		~/.julia/v0.4/AdaGram/train.sh $1 $2                           	\
		adagram_${1}_${append} 	--workers=$workers --alpha=$alpha 		\
		--dim=$dim --epochs=$epochs --window=$window --min-freq=$min_freq \
		--remove-top-k=$remove_top_k
	done
done
