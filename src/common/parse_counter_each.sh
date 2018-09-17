#!/bin/bash
# counts number of parses in each file in folder, based on newlines
# takes one arguments: directory with parse files

# usage: parse_counter_each.sh dir

for file in $1/*
do
    filename=$(basename -- "$file")
    echo $filename
    ~/MyOpenCogSources/language-learning/src/common/parse_counter.sh $file
done
