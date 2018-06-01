#!/bin/bash

for file in $PWD/$1/*
do
    start_line="$(sed -n '/start of this project gutenberg/=' 11-0.txt_split_default)"
    echo $start_line
done