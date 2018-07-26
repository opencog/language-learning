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
    default = 5
  "--min-prob"
    help = "minimum probability value to print a word sense"
    arg_type = Float64
    default = 0.05
  "--voc-fraction"
    help = "fraction of the vocabulary to print out"
    arg_type = Float64
    default = 1.0
end

args = parse_args(ARGS, s)

vm, dict = load_model(args["AdaGramFile"]);

fo = open(args["outputFile"], "w")

numWords = round(Int,V(vm) * args["voc-fraction"])
letters = "abcdefghjklmnopqrstuvwxyz" # "i" skipped on purpose bc LG dict

for v in 1:numWords
    probs = expected_pi(vm, v)
    for s in 1:T(vm)
        if probs[s] > args["min-prob"] && vm.counts[s, v] >= 1
            nn = nearest_neighbors(vm, dict, vec(vm, v, s), args["neighbors"]; exclude=[(Int32(v), s)])
            tag_main = string(letters[s % length(letters)])
            @printf(fo, "%s@%s\t%.3f\t", dict.id2word[v], tag_main, probs[s])
    	    for neighbor in nn
        		#@printf(fo, "%s@%s@%.3f ", neighbor[1], neighbor[2], neighbor[3])
                tag_neighbor = string(letters[neighbor[2] % length(letters)])
                @printf(fo, "%s@%s\t", neighbor[1], tag_neighbor)
    	    end
            for neighbor in nn
                @printf(fo, "%.3f\t", neighbor[3])
            end
            println(fo)
            for iDim in 1:M(vm)
                @printf(fo, "%s ", vm.In[:,s,v][iDim])
            end
            println(fo)
        end
    end
end

close(fo)
