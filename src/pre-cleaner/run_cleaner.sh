#!/bin/bash

# ASuMa, Apr 2018
# Usage FULL_PATH/run_cleaner -i <inputdir> -o <outputdir> [other args]
# Run from directory above your inputdir

CLEANER_PATH="`dirname \"$0\"`"

SPLIT_DIR=split_books
mkdir -p $SPLIT_DIR

for file in $PWD/$2/*
do
	filename=$(basename -- "$file")
	echo $file
    $CLEANER_PATH/split-sentences.pl < $file > "${SPLIT_DIR}/${filename}_split"
done

mkdir -p $4

$CLEANER_PATH/pre-cleaner.py $@

