#!/bin/bash

# ASuMa, Apr 2018
# Usage ./run_cleaner <inputdir> <outputdir>
# Run from directory where executable is, provide full path to inputdir
# and only name of outputdir, no full path.

for file in $1/*.txt
do
	echo $file
    ./split-sentences.pl < $file > "${file}_split"
    rm $file
done

./pre-cleaner.py -i $1 -o $2