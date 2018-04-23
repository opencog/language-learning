#!/usr/bin/env python

# ASuMa, Mar 2018
# Read parse data in MST-parser format, from reference and test files
# and evaluate the accuracy of the test parses.
# See main() documentation below for usage details

import platform
import getopt, sys
import matplotlib.pyplot as plt
import numpy as np

def version():
    """
        Prints Python version used
    """
    print("Code writen for Python3.6.4. Using: %s"%platform.python_version())

def Load_File(filename):
    """
        Loads a data file
    """
    with open(filename) as file:
        data = file.readlines()
    return data

def Get_Parses(data):
    """
        Separates parses from data into format:
        [
          [[sentence-parse1][link1-parse1][link2-parse1] ... ]
          [[sentence-parse2][link1-parse2][link2-parse2] ... ]
          ...
        ]
        Each list is splitted into tokens using space.
    """
    parses = []
    sentences = {}
    parse_num = -1
    new_flag = True
    for line in data:
        if line == "\n":
            new_flag = True
            continue
        if new_flag:
            parse_num += 1
            sentences[parse_num] = line
            new_flag = False
            parses.append([])
            continue
        parses[parse_num].append(line.split())

    return parses, sentences

def MakeSets(parse):
    """
        Gets a list with links (without full sentence) and
        and makes sets for each link's ids
    """
    link_sets = [{(link[0], link[1]), (link[2], link[3])} for link in parse]
    return link_sets

def Evaluate_Parses(test_parses, test_sentences, ref_parses, ref_sentences, verbose, ignore):
    """
        Compares test_parses against ref_parses link by link
        counting errors
    """
    skipped_parses = 0  # reference parses not found in test
    total_links = 0     # in gold standard
    #extra_links = 0     # links present in test, but not in ref
    missing_links = 0   # links present in ref, but not in test
    ignored_links = 0   # ignored links, if ignore is active

    for ref_key, ref_sentence in ref_sentences.items():
        test_key = [key for key, sentence in test_sentences.items() if value == ref_sentence]
        if len(test_key) == 0
            if verbose:
                print("Skipping sentence not found in test parses:")
                print(ref_sentence)
            skipped_parses += 1
            continue
        test_sentences.pop(test_key[0]) # reduce the size of dict to search

        current_missing = 0
        ref_sets = MakeSets(ref_parses[ref_key])  # using sets to ignore link directions
        test_sets = MakeSets(test_parses[test_key[0]])
        sent_length = str(len(ref_sent))

        # loop over every ref link and try to find it in test
        for ref_link in ref_sets:
            if ignore:
                if (('0', '###LEFT-WALL###') in ref_link) or ((sent_length, ".") in ref_link):
                    ignored_links += 1
                    continue
            total_links += 1
            if ref_link in test_sets:
                test_sets.remove(ref_link) 
            else:
                current_missing += 1 # count links not contained in test

        if verbose:
            print("Sentence: {}".format(" ".join(ref_sent)))
            print("Missing links: {}".format(current_missing))
            print("Extra links: {}".format(len(test_sets)))

        #extra_links += len(test_sets) # count links not contained in reference
        missing_links += current_missing

    score = 1 - missing_links / total_links
    print("\nParses score: {}".format(score))
    print("A total of {} links".format(total_links))
    print("A total of {} ignored links".format(ignored_links))
    print("A total of {} missing links".format(missing_links))
    #print("A total of {} extra links".format(extra_links))


def Plot_Scatter(dictio, savefile):
    """
        Calculates Pearson's coefficients and plots data in dictio
        in 2 scatter plots, into savefile.png
    """
    LG_data = []
    dist_data = []
    no_dist_data = []
    for k, value in dictio.items():
        LG_data.append(value[0])
        dist_data.append(value[1])
        no_dist_data.append(value[2])

    # calculate Pearson's coefficient for each pair
    pearR_dist = np.corrcoef(LG_data, dist_data)[1,0]
    pearR_no_dist = np.corrcoef(LG_data, no_dist_data)[1,0]

    # scatter plots
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle("FMI scatter-data")
    ax1.scatter(LG_data, dist_data, c = 'b', marker = '.', label = "R = %.4f"%(pearR_dist))
    ax1.set_title('LG vs Distance')
    ax1.set(xlabel = 'LG data', ylabel = 'window data')
    ax1.legend()
    ax1.axis('scaled')
    ax2.scatter(LG_data, no_dist_data, c = 'r', marker = '.', label = "R = %.4f"%(pearR_no_dist))
    ax2.set(xlabel = 'LG data')
    ax2.set_title('LG vs No-Distance')
    ax2.legend()
    ax2.axis('scaled')
    plt.savefig(savefile + ".png")

def main(argv):
    """
        Evaluates parses compared to given gold standard (GS).
        For each parse, loops through all links in GS and checks if those
        2 word-instances are also connected in parse to evaluate.

        Parses must be in format:
        Sentence to evaluate
        # word1 # word2
        # word2 # word3
        ...

        Another sentence to evaluate
        # word1 # word2
        ...

        Usage: ./parse_evaluator.py -t <testfile> -r <reffile> [-v] [-i]

        testfile        file with parses to evaluate
        goldfile        file with reference (gold standard) parses
        -v              verbose
        -i              don't ignore LEFT-WALL and end-of-sentence dot, if any

    """

    version()

    test_file = ''
    ref_file = ''
    verbose = False
    ignore_WALL = True

    try:
        opts, args = getopt.getopt(argv, "ht:r:vi", ["test=", "reference=", "verbose", "ignore"])
    except getopt.GetoptError:
        print("Usage: ./parse_evaluator.py -t <testfile> -r <reffile> [-v] [-i]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage: ./parse_evaluator.py -t <testfile> -r <reffile>")
            sys.exit()
        elif opt in ("-t", "--test"):
            test_file = arg
        elif opt in ("-r", "--reference"):
            ref_file = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-i", "--ignore"):
            ignore_WALL = False

    test_data = Load_File(test_file)
    test_parses, test_sentences = Get_Parses(test_data) 
    ref_data = Load_File(ref_file)
    ref_parses, ref_sentences = Get_Parses(ref_data) 
    Evaluate_Parses(test_parses, test_sentences, ref_parses, ref_sentences, verbose, ignore_WALL)

if __name__ == '__main__':
    main(sys.argv[1:])