#!/bin/bash
# counts number of parses in file, based on newlines
# takes one arguments: file to count parses

# usage: parse_counter.sh file

# To count all parses in all files inside some folder, run in command line:
# cat FOLDER/* | parse_counter.sh

uniq $1 | grep -cvP '\S'