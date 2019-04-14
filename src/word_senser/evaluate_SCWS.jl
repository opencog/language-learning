# ASuMa Sept, 2018
# This script takes an AdaGram model and evalautes 4 similarity measures
# using the SCWS dataset (Huang et al. 2012)

# usage:
#   evaluate_SCWS.sh model(file or dir) 
#                   output-dir [--joiner=@] [--min-prob=0.3] [--window=4]
# see arg table for meaning of parameters

#push!(LOAD_PATH, "./src/")

function disambiguate_word(vm, dict, word, valid_context, window)
"""
    Disambiguates a valid word using valid context
"""
        return disambiguate(vm, dict, word, valid_context)
end

function similarity(vm, dict, w1, s1, w2, s2)
"""
    Calculates cosine distance between two sense vectors
"""
    v1 = dict.word2id[w1]
    v2 = dict.word2id[w2]
    sense_vec1 = vec(vm, v1, s1)
    sense_vec2 = vec(vm, v2, s2)
    return dot(sense_vec1, sense_vec2)
end

function evaluate_entry(vm, dict, word1, word2, context1, context2; min_prob=1e-2)
"""
    Evaluates 4 similarity measures for a pair or words
"""
    priors1 = expected_pi(vm, dict.word2id[word1])
    priors2 = expected_pi(vm, dict.word2id[word2])
    posteriors1 = disambiguate(vm, dict, word1, context1)
    posteriors2 = disambiguate(vm, dict, word2, context2)

    # AvgSim & MaxSim (no context involved)
    # AvgSimC & MaxSimC (context taken into account)
    similarities = []
    similaritiesC = []
    for s1 in 1:T(vm)
        if priors1[s1] > min_prob
            for s2 in 1:T(vm)
                if priors2[s2] > min_prob
                    sim = similarity(vm, dict, word1, s1, word2, s2)
                    push!(similarities, sim)
                    push!(similaritiesC, sim * posteriors1[s1] * posteriors2[s2])
                end
            end
        end
    end
    AvgSim = mean(similarities)
    MaxSim = maximum(similarities)
    AvgSimC = sum(similaritiesC)

    best_sense1 = findmax(posteriors1)[2]
    best_sense2 = findmax(posteriors2)[2]
    MaxSimC = similarity(vm, dict, word1, best_sense1, word2, best_sense2)

    return AvgSim, MaxSim, AvgSimC, MaxSimC
end

function words_in_model(dict, word1, word2)
"""
    Checks if both words in pair are included in vector model
"""
    if (word1 in dict.id2word) && (word2 in dict.id2word)
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

function build_context(dict, tokens, window)
"""
    Builds a valid context array
"""
    context = tokens
    filter!(x -> x in dict.id2word, context)
    if length(context) > window
        context = context[1:window]
    end
    return context
end


function filter_context(dict, text, window, word)
"""
    Prepares context of size 2 * window with only valid words
"""
    split_text = split(text, "<b> " * word * " </b>") # remove current word
    left_text = reverse(split(split_text[1]))
    right_text = split(split_text[2])
    left_context = build_context(dict, left_text, window)
    right_context = build_context(dict, right_text, window)
    return vcat(left_context, right_context)
end

function evaluate_model(local_model, window, SCWS_PATH)
"""
    Evaluates the given model using a context of size window
"""

    data = load_SCWS(SCWS_PATH)
    vm, dict = load_model(local_model);

    Avg_list = Float32[]
    Max_list = Float32[]
    AvgC_list = Float32[]
    MaxC_list = Float32[]
    similarities_GS = Float32[]

    for i = 1:size(data)[1]
        entry = data[i,:]
        word1 = lowercase(string(entry[2]))
        word2 = lowercase(string(entry[4]))
        text1 = lowercase(entry[6])
        text2 = lowercase(entry[7])
        if !words_in_model(dict, word1, word2)
            #println("At least one word not in model for entry: ", i)
            continue
        end

        context1 = filter_context(dict, text1, window, word1)
        context2 = filter_context(dict, text2, window, word2)
        if length(context1) == 0 || length(context2) == 0
            println("Context invalid for entry id: ", i)
            continue
        end

        scores = evaluate_entry(vm, dict, word1, word2, context1, context2)
        push!(Avg_list, scores[1])
        push!(Max_list, scores[2])
        push!(AvgC_list, scores[3])
        push!(MaxC_list, scores[4])
        push!(similarities_GS, entry[8])
    end

    println("--------------------------------------------")
    println("Processed pairs: ", length(Avg_list))
    println("--------------------------------------------")
    println("Spearman's coeff for AvgSim: ", corspearman(Avg_list, similarities_GS))
    println("Spearman's coeff for MaxSim: ", corspearman(Max_list, similarities_GS))
    println("Spearman's coeff for AvgSimC: ", corspearman(AvgC_list, similarities_GS))
    println("Spearman's coeff for MaxSimC: ", corspearman(MaxC_list, similarities_GS))
    println("--------------------------------------------")
end


using ArgParse
using AdaGram
using StatsBase

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