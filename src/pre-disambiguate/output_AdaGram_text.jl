# This script takes an AdaGram model
# and generates a file with all word senses and their nearest neighbors
# ASuMa 2018

#push!(LOAD_PATH, "./src/")

using ArgParse
using AdaGram

s = ArgParseSettings()

@add_arg_table s begin
  "AdaGramFile"
    help = "File with AdaGram model"
    arg_type = AbstractString
    required = true
  "outputFile"
    help = "File to output word senses"
    arg_type = AbstractString
    required = true
  "--neighbors"
    help = "Number or nearest neighbors to print"
    arg_type = Int64
    default = 10
  "--min_prob"
    help = "minimum probability value to print a word sense"
    arg_type = Float64
    default = 0.05
  "--voc_fraction"
    help = "fraction of the vocabulary to print out"
    arg_type = Float64
    default = 1.0
    
end

args = parse_args(ARGS, s)

vm, dict = load_model(args["AdaGramFile"]);

fo = open(args["outputFile"], "w")

numWords = round(Int,V(vm) * args["voc_fraction"])

for v in 1:numWords
    probs = expected_pi(vm, v)
    for s in 1:T(vm)
        if probs[s] > args["min_prob"]
            nn = nearest_neighbors(vm, dict, vec(vm, v, s), args["neighbors"]; exclude=[(Int32(v), s)])
            @printf(fo, "%s\t", dict.id2word[v])
	    for neighbor in nn
		@printf(fo, "%s ", neighbor[1])
	    end
	    @printf(fo, "\n")
        end
    end
end

close(fo)
