#!/bin/bash

# ASuMa, Apr 2018
# Usage ./run_cleaner <inputdir> <outputdir>

for file in $1/*.txt
do
	echo $file
    ./split-sentences.pl < $file > "${file}_split"
    rm $file
done

./pre-cleaner.py -i $1 -o $2