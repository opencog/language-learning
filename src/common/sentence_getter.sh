#!/bin/bash
# outputs to file the first line in each block of
# text separated by newlines. Useful to get
# sentences only from a parsed file (ull format)

# takes two arguments: file to get lines from, file to ouput firs lines

# usage: sentence_getter.sh file outfile

# To get all first-lines in all files inside some folder, run in command line:
# cat FOLDER/* | sentence_getter.sh

uniq $1 | awk -v RS='\n\n' -v FS='\n' '{printf "%s\n\n",$1}' > $2
# uniq removes all duplicated newlines
# awk 	-v RS defines the record separator as an empty line
#     	-v FS defines the field separator as eol
#	 	printf prints only field $1, the first line of the block