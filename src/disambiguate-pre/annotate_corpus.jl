# This script takes a corpus and an AdaGram model
# and outputs an annotated corpus with word senses, if there is more
# than one for a word
# ASuMa May, 2018

#push!(LOAD_PATH, "./src/")

function annotate_word(outfile, separator, threshold, vm, dict, word, context)
"""
    Writes word in the outfile.
    If the word has more than one sense above threshold in vm model, 
    its context is used to get the current sense, and
    it's annotated with separator and sense number
"""
    output_word = word
    id = get(dict.word2id, word, -1)
    if id != -1
        priors = expected_pi(vm, id)
        if length(find(priors .> threshold)) > 1
            probs = disambiguate(vm, dict, word, context)
            best_sense = findmax(probs)[2]
            output_word = word * separator * string(best_sense)
        end
    end
    write(outfile, output_word * " ")
end

function annotate_file(corpus, outfile, vm, dict, separator, min_prob, win)
"""
   Goes through lines in corpus and calls annotate_word to re-write corpus 
"""
    open(corpus, "r") do fi
        open(outfile, "w") do fo
            for line in eachline(fi)
                split_line = split(line)
                #println(split_line)
                for i in enumerate(split_line)
                    llim = max(1, i[1] - win)
                    ulim = min(length(split_line), i[1] + win)
                    context = split_line[llim:ulim]
                    deleteat!(context, i[1] + 1 - llim)
                    rm_index = []
                    for word in enumerate(context)
                        if get(dict.word2id, word[2], -1) == -1
                            push!(rm_index, word[1])
                        end
                    end
                    deleteat!(context, rm_index)
                    #println(context)
                    annotate_word(fo, separator, min_prob, vm, dict, i[2], context)
                end
                seek(fo, position(fo) - 1)
                write(fo, "\n")
            end
        end
    end
end

using ArgParse
using AdaGram

s = ArgParseSettings()

@add_arg_table s begin
  "AdaGramFile"
    help = "File with AdaGram model"
    arg_type = AbstractString
    required = true
  "corpus-dir"
    help = "Directory with files to annotate"
    arg_type = AbstractString
    required = true
  "output-dir"
    help = "Directory to output annotated corpus"
    arg_type = AbstractString
    required = true
  "--joiner"
    help = "Symbol to annotate word senses"
    arg_type = AbstractString
    default = "@"
  "--min-prob"
    help = "Min probability of second sense to consider a word ambiguous"
    arg_type = Float64
    default = 0.05
  "--window"
    help = "Size of window to look for context"
    arg_type = Int64
    default = 4
end

args = parse_args(ARGS, s)

vm, dict = load_model(args["AdaGramFile"]);

separator = args["joiner"]
min_prob = args["min-prob"]
win = args["window"]
corpus_dir = args["corpus-dir"]
output_dir = args["output-dir"]
if !isdir(output_dir) 
    mkdir(output_dir) 
end

for file in readdir(corpus_dir)
    annotate_file(corpus_dir * "/" * file, output_dir * "/" * file * "_disamb", vm, dict, separator, min_prob, win)
end

