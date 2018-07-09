#!/usr/bin/env python

# ASuMa, Mar 2018
# Read parse data in MST-parser format, from reference and test files
# and evaluate the accuracy of the test parses.
# See main() documentation below for usage details

import platform
import getopt, sys

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
    print("Finished loading")

    # remove initial newlines, if any
    # while data[0] == "\n":
    #     data.pop(0)

    return data

def Get_Parses(data):
    """
        Reads parses from data, counting number of parses by newlines
        - num_parses: number of parses in data
        - parses: a list of lists containing the split links of each parse
        [
          [[link1-parse1][link2-parse1] ... ]
          [[link1-parse2][link2-parse2] ... ]
          ...
        ]
        Each list is splitted into tokens using space.
    """
    parses = []
    parse_num = -1
    sent_lengths = []
    new_flag = True
    for line in data:
        if line == "\n":
            # get rid of sentences with no links
            new_flag = True
            continue
        if new_flag:
            new_flag = False
            sent_lengths.append(len(line.split()))
            parses.append([])
            parse_num += 1
            continue
        parses[parse_num].append(line.split())

    return parses, sent_lengths

def MakeSets(parse):
    """
        Gets a list with links (without full sentence)
        and makes sets for each link's ids
    """
    link_sets = [{(link[0], link[1]), (link[2], link[3])} for link in parse]
    return link_sets

def Evaluate_Parses(test_parses, ref_parses, ref_lengths, verbose, ignore):
    """
        Compares test_parses against ref_parses link by link
        counting errors
    """
    evaluated_parses = 0 
    total_links = 0     # in gold standard
    #extra_links = 0     # links present in test, but not in ref
    missing_links = 0   # links present in ref, but not in test
    ignored_links = 0   # ignored links, if ignore is active
    score = 0           # parse quality counter

    def Remove_words(link_sets):
        """
            replace words in link with empty string
            to compare links with sense-disambiguated words
        """
        wordless_sets = []
        for link in link_sets:
            wordless_sets.append({(link[0][0], ""), (link[1][0], "")})
        return wordless_sets


    for ref_parse, test_parse, sent_length in zip(ref_parses, test_parses, ref_lengths):

        current_missing = 0
        current_evaluated = 0
        current_ignored = 0
        ref_sets = MakeSets(ref_parse)  # using sets to ignore link directions
        test_sets = MakeSets(test_parse)

        ref_wordless = Remove_words(ref_sets)
        test_wordless = Remove_words(test_sets)
        # loop over every ref link and try to find it in test
        for ref_link in ref_sets:
            total_links += 1
            if ignore:
                if (('0', '###LEFT-WALL###') in ref_link) or ((str(sent_length), ".") in ref_link):
                    current_ignored += 1
                    continue
            current_evaluated += 1
            if ref_wordless in test_wordless:
                print("found: {}".format(ref_link))
                test_sets.remove(ref_link) 
            else:
                print("missing: {}".format(ref_link))
                current_missing += 1 # count links not contained in test

        # skip parse if there are no links left after ignore
        if current_ignored == len(ref_sets):
            continue

        evaluated_parses += 1

        if verbose:
            #print("Sentence: {}".format(" ".join(ref_sent)))
            print("Missing links: {}".format(current_missing))
            print("Extra links: {}".format(len(test_sets)))

        ignored_links += current_ignored
        score += 1 - float(current_missing) / float(current_evaluated) # adds this parse's relative score
        #extra_links += len(test_sets) # count links not contained in reference
        missing_links += current_missing

    score /= evaluated_parses # averages the score
    print("\nParse quality: {:.2%}".format(score))
    print("A total of {} parses evaluated, {:.2%} of reference file".format(evaluated_parses, float(evaluated_parses) / len(ref_parses)))
    print("A total of {} links".format(total_links))
    print("{:.2f} ignored links per sentence".format(ignored_links / evaluated_parses))
    print("{:.2f} missing links per sentence".format(missing_links / evaluated_parses))
    #print("{:.2f} extra links per sentence\n".format(extra_links / evaluated_parses))
    #print("A total of {} extra links".format(extra_links))

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
    test_parses, test_lenghts = Get_Parses(test_data) 
    ref_data = Load_File(ref_file)
    ref_parses, ref_lengths = Get_Parses(ref_data) 
    if len(test_parses) != len(ref_parses):
        sys.exit("ERROR: Number of parses differs in files")
    Evaluate_Parses(test_parses, ref_parses, ref_lengths, verbose, ignore_WALL)

if __name__ == '__main__':
    main(sys.argv[1:])