#!/bin/bash
# creates frequency table for words in file
# takes two arguments: corpus and otuput file name

# usage: ./freq_table.sh corpus output

tr " " "\n" < $1 | tr "." "\n" | tr "," "\n" | tr ";" "\n" | tr "!" "\n" | tr "?" "\n" | tr ":" "\n" | sort | uniq -c | awk '{print $2"\t"$1}' > $2
