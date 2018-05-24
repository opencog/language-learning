# This script takes a corpus and an AdaGram model
# and outputs an annotated corpus with word senses, if there is more
# than one for a word
# ASuMa May, 2018

#push!(LOAD_PATH, "./src/")

function annotate_word(outfile, word, context, vm, dict)

end

function annotate_file(corpus, vm, dict, separator, min_prob, win)
    outfile = corpus * "_disamb"
    open(corpus, "r") do fi
        open(outfile, "r") do fo
            for line in eachline(fi)
                split_line = split(line)
                #println(split_line)
                for i in enumerate(split_line)
                    llim = max(1, i[1] - win)
                    ulim = min(length(split_line), i[1] + win)
                    context = split_line[llim:ulim]
                    deleteat!(context, i[1] + 1 - llim)
                    #println(context)
                    annotate_word(fo, i[2], context, vm, dict)
                end
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
    help = "Minimum probability value to print a word sense"
    arg_type = Float64
    default = 0.05
  "--window"
    help = "Size of window to look for context"
    arg_type = Int64
    default = 2
end

args = parse_args(ARGS, s)

vm, dict = load_model(args["AdaGramFile"]);

separator = args["joiner"]
min_prob = args["min-prob"]
win = args["window"]
corpus_dir = args["corpus-dir"]

for file in readdir(args["corpus-dir"])
    annotate_file(corpus_dir * "/" * file, vm, dict, separator, min_prob, win)
end