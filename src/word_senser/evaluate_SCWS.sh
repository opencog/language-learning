#!/bin/bash

OUTPUT_PATH="`dirname \"$0\"`"
"$HOME/.julia/v0.4/AdaGram/run.sh" "$OUTPUT_PATH/evaluate_SCWS.jl" "$@"

