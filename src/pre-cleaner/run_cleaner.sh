#!/bin/bash

# ASuMa, Apr 2018
# Usage FULL_PATH/run_cleaner <inputdir> <outputdir>
# Run from directory above your inputdir

CLEANER_PATH="`dirname \"$0\"`"

for file in $PWD/$1/*
do
	echo $file
    $CLEANER_PATH/split-sentences.pl < $file > "${file}_split"
    rm $file
done

mkdir -p $2

$CLEANER_PATH/pre-cleaner.py -i $1 -o $2