#!/bin/bash

# ASuMa, Apr 2018
# Usage FULL_PATH/run_cleaner <inputdir> <outputdir> --nosplitter [other args for pre-cleaner.py]
# Run from directory above your inputdir


CLEANER_PATH="`dirname \"$0\"`"

INPUT_DIR=$1
OUTPUT_DIR=$2

if [ "$3" == "nosplitter" ]
then
	shift
else
	SPLIT_DIR=split_books
	mkdir -p $SPLIT_DIR

	for file in $PWD/${INPUT_DIR}/*
	do
		filename=$(basename -- "$file")
		echo $file
	    $CLEANER_PATH/split-sentences.pl < $file > "${SPLIT_DIR}/${filename}_split"
	done
	INPUT_DIR=$SPLIT_DIR
fi
shift 2

mkdir -p $OUTPUT_DIR

$CLEANER_PATH/pre-cleaner.py -i $INPUT_DIR -o $OUTPUT_DIR $@
