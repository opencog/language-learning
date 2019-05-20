#!/bin/bash
# Outputs to file the same blocks, but removing
# first field at the beginning of it.
# Useful for cleaning ull files by DNN with initial LEFT-WALL

# takes two arguments: file to get blocks from, file to blocks with no WALL

# usage: rm_LEFTWALL.sh file outfile

uniq $1 | awk -v RS='\n\n' 'sub("^" $1 FS, _) {print $0 "\n"}' > $2
# uniq removes all duplicated newlines
# awk 	-v RS defines the record separator as an empty line
#		then awk removes first field at the beginning of the block