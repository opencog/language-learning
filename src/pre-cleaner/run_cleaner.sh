#!/bin/bash

# ASuMa, Apr 2018
# Usage FULL_PATH/run_cleaner -i <inputdir> -o <outputdir> [other args]
# Run from directory above your inputdir

CLEANER_PATH="`dirname \"$0\"`"

for file in $PWD/$2/*
do
	echo $file
    $CLEANER_PATH/split-sentences.pl < $file > "${file}_split"
    rm $file
done

mkdir -p $4

$CLEANER_PATH/pre-cleaner.py $@