# ASuMa May, 2018
# This script takes a directory with corpus files and one or more
# AdaGram model(s) to annotate the corpus.
# It outputs the corpus files annotated with word senses, if there is more
# than one sense above the threshold for a given word

# usage:
#   annotate_corpus model(file or dir) corpus-dir 
#                   output-dir [--joiner=@] [--min-prob=0.3] [--window=4]
# see arg table for meaning of parameters

#push!(LOAD_PATH, "./src/")

function annotate_word(outfile, separator, threshold, vm, dict, word, context)
"""
    Writes word in the outfile.
    If the word has more than one sense above threshold in vm model, 
    its context is used to get the current sense, and
    it's annotated with separator and sense number
"""
    letters = "abcdefghjklmnopqrstuvwxyz" # "i" skipped on purpose bc LG dict
    output_word = word
    id = get(dict.word2id, word, -1)
    if id != -1
        priors = expected_pi(vm, id)
        if length(find(priors .> threshold)) > 1
            probs = disambiguate(vm, dict, word, context, true, threshold)
            best_sense = findmax(probs)[2]
            tag = string(letters[best_sense % length(letters)])
            output_word = word * separator * tag
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
                if line == "\n"
                    write(fo, "\n")
                end
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
  "model"
    help = "File or directory with AdaGram model(s)"
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
    default = 0.3
  "--window"
    help = "Size of window to look for context"
    arg_type = Int64
    default = 4
end

args = parse_args(ARGS, s)

separator = args["joiner"]
min_prob = args["min-prob"]
win = args["window"]
corpus_dir = args["corpus-dir"]
output_dir = args["output-dir"]
model = args["model"]
if !isdir(output_dir) 
    mkdir(output_dir) 
end

temp = "temp_folder"
# if model is single file, copy it in a temp folder
if !isdir(model)
    mkdir(temp)
    cp(model, temp * "/" * model)
    model = temp
end

for curr_model in readdir(model)

    vm, dict = load_model(model * "/" * curr_model);

    for file in readdir(corpus_dir)
        println("Annotating " * file * " with model " * curr_model)
        corpus_file = corpus_dir * "/" * file
        output_file = output_dir * "/" * file * curr_model * "_disamb"
        annotate_file(corpus_file, output_file, vm, dict, separator, min_prob, win)
    end

end

# if temp folder was created, delete it
if isdir(temp)
    rm(temp, recursive=true)
end