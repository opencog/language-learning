#!/bin/bash
# Outputs to file the same blocks, but removing
# first field at the beginning of it.
# Useful for cleaning ull files by DNN with initial LEFT-WALL

# takes one argument: file or directory with files to remove LW
# outputs processed files in directory with same name, appened by "-OLW"

# usage: rm_LEFTWALL.sh <file or dir>

newdir=$1"-0LW";
echo $newdir
mkdir -p $newdir;

if [ -d "$1" ]
then
	for file in $1/*
	do
	    filename=$(basename -- "$file");
	    echo $filename;
		uniq $filename | awk -v RS='\n\n' 'sub("^" $1 FS, _) {print $0 "\n"}' > $newdir/$filename;
	done
elif [ -f "$1" ]
then
	uniq $1 | awk -v RS='\n\n' 'sub("^" $1 FS, _) {print $0 "\n"}' > $newdir/$1;
else echo "$1 is not valid";
	exit 1;
fi

# uniq removes all duplicated newlines
# awk 	-v RS defines the record separator as an empty line
#		then awk removes first field at the beginning of the block