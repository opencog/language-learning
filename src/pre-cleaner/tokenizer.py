#! /usr/bin/env python
# -*- coding: utf8 -*-

# ASuMa, Mar 2018
# Tokenizer that uses LG functionality
# Usage: tokenizer.py -i <inputfile> -o <outputfile>


import getopt, sys
from linkgrammar import Linkage, Sentence, ParseOptions, Dictionary, Clinkgrammar as clg

any_dict = Dictionary('any') # Opens dictionary only once
po = ParseOptions(min_null_count=0, max_null_count=999)

def main(argv):
    """
        Tokenizer procedure that uses LG tokenizer with python bindings

        Usage: tokenizer.py -i <inputfile> -o <outputfile>

        inputfile           Name of inputfile
        outputfile          Name of ouputfile
        -S                  Don't remove sentence splitters added by 
                            pre-cleaner.py (default removes them)
    """

    inputfile = ''
    outputfile = ''
    remove_splitter = True

    try:
        opts, args = getopt.getopt(argv, "hi:o:S", ["ifile=", "ofile=", 
            "Splits"])
    except getopt.GetoptError:
        print("Usage: tokenizer.py -i <inputfile> -o <outputfile> [-S]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: tokenizer.py -i <inputfile> -o <outputfile> [-S]')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-S", "--Splits"):
            remove_splitter = False

    sentences = Load_Files(inputfile)

    fo = open(outputfile, "w")
    for sentence in sentences:
        if sentence == "<P>\n":
            if remove_splitter == True:
                continue
        tokenized_sentence = Tokenize_Sentence(sentence, po)
        Write_Output_Sentence(fo, tokenized_sentence)
    fo.close()

def Tokenize_Sentence(sentence, po):
    """
        Tokenizes the given sentence using LG grammar bindings
    """
    tokenized_sentence = ""
    sent = Sentence(sentence, any_dict, po)
    linkages = sent.parse()
    #linkage = Linkage(0, sent, po)
    for linkage in linkages:
        num_words = linkage.num_of_words()
        for i in range(num_words - 1): # index shift ignores ###LEFT-WALL
            word_start = linkage.word_byte_start(i + 1)
            word_end = linkage.word_byte_end(i + 1)
            tokenized_sentence += sentence[word_start:word_end] + " "
        break
    tokenized_sentence += "\n"
    return tokenized_sentence


def Load_Files(filename):
    """
        Loads file already sentence-splitted, returning a list of all sentences
    """
    file = open(filename, "r")
    sentences = file.readlines()
    file.close()
    return sentences

def Write_Output_Sentence(fo, sentence):
    """
        writes sentence to the output file
    """
    fo.write(sentence)

if __name__ == "__main__":
    main(sys.argv[1:])