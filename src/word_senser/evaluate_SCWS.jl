# ASuMa Sept, 2018
# This script takes an AdaGram model and evalautes 4 similarity measures
# using the SCWS dataset (Huang et al. 2012)

# usage:
#   evaluate_SCWS.sh model(file or dir) 
#                   output-dir [--joiner=@] [--min-prob=0.3] [--window=4]
# see arg table for meaning of parameters

#push!(LOAD_PATH, "./src/")

function disambiguate_word(vm, dict, word, context, window)
"""
    Disambiguates a valid word using context of size window.
    If some words in context don't exist in the model, they get replaced
    if possible
"""
        return disambiguate(vm, dict, word, valid_context)
end

function process_entry()
    # id = get(dict.word2id, word, -1)
    # if id != -1
    #     priors = expected_pi(vm, id)
    #     best_sense = findmax(probs)[2]
    return true
end

function words_in_model(vm, dict, word_pair)
"""
    Checks if both words in pair are included in vector model
"""
    if (word_pair[2] in dict.id2word) && (word_pair[4] in dict.id2word)
        return true
    else
        return false
    end
end

function load_SCWS(path)
""" 
    Loads SCWS database in path into a matrix where each row is of the form:
    [<id> <word1> <POS of word1> <word2> <POS of word2> <word1 in context> <word2 in context> <average human rating> <10 individual human ratings>]
"""
    database = []
    open(path, "r") do fi
        database = readdlm(fi, '\t')
    end
    return database
end

function evaluate_model(local_model, window, SCWS_PATH)
"""
    Evaluates the given model using a context of window size when needed
"""

    data = load_SCWS(SCWS_PATH)
    vm, dict = load_model(local_model);

    processed_pairs = 0
    for i = 1:size(data)[1]
        entry = data[i,:]
        if !words_in_model(vm, dict, entry)
            continue
        end

        #process_entry(vm, dict, word_pair)
        processed_pairs += 1
    end
    println("Processed pairs: ", processed_pairs)

end


using ArgParse
using AdaGram

s = ArgParseSettings()

@add_arg_table s begin
  "model"
    help = "File or directory with AdaGram model(s)"
    arg_type = AbstractString
    required = true
  "--window"
    help = "Size of context window"
    arg_type = Int64
    default = 4
end

args = parse_args(ARGS, s)

#SCWS_PATH = "/home/andres/SCWS_dataset/test"
SCWS_PATH = "/home/andres/SCWS_dataset/ratings_unquoted.txt"
win = args["window"]
model = args["model"]
temp_folder = "temp_folder"

# if model is single file, copy it in a temp folder
if !isdir(model)
    if isdir(temp_folder)
        rm(temp_folder, recursive = true)
    end
    mkdir(temp_folder)
    cp(model, temp_folder * "/" * model)
    model = temp_folder
end

for curr_model in readdir(model)
    println("Evaluating model: " * curr_model)
    evaluate_model(model * "/" * curr_model, win, SCWS_PATH)
end

# if temp folder was created, delete it
if isdir(temp_folder)
    rm(temp_folder, recursive=true)
end