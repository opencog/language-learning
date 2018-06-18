#!/bin/bash

# ASuMa, June 2018
# Usage FULL_PATH/cleaner_pipeline <inputdir> <outputdir> [more args to run_cleaner]
# Run from directory above your inputdir

CLEANER_PATH="`dirname \"$0\"`"

HEADLESS_DIR=headless_books

mkdir -p $HEADLESS_DIR

$CLEANER_PATH/header_remover.sh $1 $HEADLESS_DIR

$CLEANER_PATH/run_cleaner.sh $@
