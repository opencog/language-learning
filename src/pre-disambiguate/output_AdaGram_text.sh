#!/bin/bash

OUTPUT_PATH="`dirname \"$0\"`"
echo $OUTPUT_PATH
"$HOME/.julia/v0.4/AdaGram/run.sh" "$OUTPUT_PATH/output_AdaGram_text.jl" "$@"