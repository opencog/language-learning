#! /usr/bin/env python
# -*- coding: utf8 -*-

# ASuMa, Aug 2018
# Converts dependency parses from treebank format to links format
# See main() documentation


import getopt, sys
import os

outputdir = ''
max_length = 25 # default value

def main(argv):
    """
        Converts dependency parses from treebank format to links format

        Usage: tree2links.py -i <inputdir> -o <outdir> [-l <max-length> ][-t <textdir>]

        inputdir           Directory with treebank formatted files
        outdir             Directory to write links format files
        max-length         Maximum length of sentence to be processed
        textdir            Path to write corpus text
    """

    inputdir = ''
    textdir = ''
    ft = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:l:t:", ["inputdir=", "outdir=", "max-length", "textdir="])
    except getopt.GetoptError:
        print("Usage: tokenizer.py -i <inputdir> -o <outdir> [-l <max-lenght> ][-t <textdir>]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: tokenizer.py -i <inputdir> -o <outputdir> [-l <max-lenght> ][-t <textdir>]')
            sys.exit()
        elif opt in ("-i", "--inputdir"):
            inputdir = arg
        elif opt in ("-o", "--outdir"):
            outdir = arg
        elif opt in ("-l", "--max-length"):
            max_length = arg
        elif opt in ("-t", "--textdir"):
            textdir = arg
            if not os.path.exists(textdir):
                os.makedirs(textdir)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for inputfile in os.listdir(inputdir):

        if textdir != '':
            textfile = textdir + "/" + inputfile + ".txt"
            ft = open(textfile, "w")
        outfile = outdir + "/" + inputfile + ".ull"
        fo = open(outfile, "w")

        data = Load_Files(inputdir + "/" + inputfile)
        lines_parse = []
        for line in data:
            if line == "\n": # end of parse
                Process_Parse(lines_parse, fo, ft)
                lines_parse = []
            else:
                lines_parse.append(line)
        Process_Parse(lines_parse, fo, ft) # final parse

        fo.close()
        if textdir != '':
            ft.close()

def Process_Parse(parse, f_parse, f_sent):
    """
        Processes the given parse and writes it in links format
        into f_parse file.
        If requested, also writes the sentences in f_sent, to get
        the raw corpus from a treebank file.
    """

    # Parse not processed if it's longer than max_length
    if len(parse) > max_length:
        return

    sentence = []
    for line in parse:
        sentence.append(line.split()[0])
    
    Write_Output_Sentence(f_parse, ' '.join(sentence) + '\n')
    if f_sent != '':
        Write_Output_Sentence(f_sent, ' '.join(sentence) + '\n\n')

    sentence.insert(0, "###LEFT-WALL###") # adds left wall in pos 0

    # need to traverse again, now that all sentence is known
    for index, line in enumerate(parse):
        linked = line.split()[2]
        link = [str(index + 1), sentence[index + 1], linked, sentence[int(linked)]]
        Write_Output_Sentence(f_parse, ' '.join(link) + '\n')

    Write_Output_Sentence(f_parse, '\n')

def Load_Files(filename):
    """
        Loads a data file
    """
    with open(filename) as file:
        data = file.readlines()
    print("Finished loading")

    return data

def Write_Output_Sentence(fo, sentence):
    """
        writes sentence to the output file
    """
    fo.write(sentence)

if __name__ == "__main__":
    main(sys.argv[1:])