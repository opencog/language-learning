#!/bin/bash
# counts number of parses in file, based on newlines
# takes one arguments: file to count parses

# usage: parse_counter.sh file

# To count all parses in all files inside some folder, run in command line:
# cat FOLDER/* | parse_counter.sh

if [ -d "$1" ]
then 
	for file in $1/*
	do
	    echo "Counts for $file"
	    uniq $file | grep -cvP '\S'
	done
	echo "Counts for whole directory:"
	cat $1/* | uniq | grep -cvP '\S'
elif [ -f "$1" ]
then 
	echo "Counts for $1"
	uniq $1 | grep -cvP '\S';
else echo "$1 is not valid";
	exit 1
fi