#!/bin/bash

# This file lets do sequential training of an AdaGram model with a range
# of parameters.
# Usage: ./train_multiple_adagram <corpusdir> <dictionary> <outputdir>
# ASuMa, May 2018

ADAGRAM_PATH=~/.julia/v0.4/AdaGram
declare -a windows=(5)
declare -a alphas=(0.9 1.1 1.3)
workers=8
dim=300
epochs=1000
min_freq=4
remove_top_k=2

mkdir -p $3

# As AdaGram trains with a single file, we merge all files in
# corpusdir into one file
cat ${1}/* > whole_corpus

for window in "${windows[@]}"
do
	for alpha in "${alphas[@]}"
	do
		append=WO${workers}D${dim}E${epochs}M${min_freq}A${alpha}W${window}R${remove_top_k}
		${ADAGRAM_PATH}/train.sh whole_corpus $2                           	\
		${3}/adagram_${append} 	--workers=$workers --alpha=$alpha 		\
		--dim=$dim --epochs=$epochs --window=$window --min-freq=$min_freq \
		--remove-top-k=$remove_top_k
	done
done

rm whole_corpus
