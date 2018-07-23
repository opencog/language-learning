#!/usr/bin/env python

# ASuMa, May 2018
# Modified from AdaGram's test-all.py to evaluate WSD in sense-annotated
# corpora inside a given directory, using a gold standard file, 
# which can be laborious to create.
# Similarly to AdaGram (http://proceedings.mlr.press/v51/bartunov16.pdf), 
# three metrics are used: V-Measure, F-score and ARI.

# "Usage: ./evaluate_WSD.py -t <testdir> -r <reffile> [-s <separator>]"
# where <separator> is the character used to annotate the file

import numpy as np
import sys
import os
import subprocess
import itertools
from sklearn.metrics import adjusted_rand_score,v_measure_score

def get_pairs(labels):
    """
        For the labels of a given word, creates all possible pairs 
        of labels that match sense
    """
    result = []
    unique = np.unique(labels)
    for label in unique:
        ulabels = np.where(labels==label)[0]
        # handles when a word sense has only one occurrence
        if len(ulabels) == 1:
            # returns the instance paired with itself, so it can be counted
            result.append((ulabels[0], ulabels[0]))
        else:
            for p in itertools.combinations(ulabels, 2):
                result.append(p)
    return result

def compute_fscore(true, pred):
    """
        Computes f-score for a word, given predicted and true senses 
    """
    one_sense = False
    true_pairs = get_pairs(true)
    pred_pairs = get_pairs(pred)
    unique_true = np.unique(true_pairs)
    unique_pred = np.unique(pred_pairs)

    # if word should not be disambiguated
    if len(unique_true) == 1:
        true_pos = 0
        false_neg = 0
        if len(unique_pred) == 1:
            false_pos = 0 # not disambiguated
        else:
            false_pos = len(true) # falsely disambiguated
    else:
        set_true_pairs = set(true_pairs)
        true_pos = len(set_true_pairs.intersection(pred_pairs)) # correct disamb
        false_neg = len(set_true_pairs) - true_pos # missing disamb
        false_pos = len(set(pred_pairs)) - true_pos # incorrect disamb

    return true_pos, false_neg, false_pos

def read_answers(filename, sep):
    """
        Read word-sense-annotated file and create data structure
        that translates each word sense to an id
    """
    with open(filename, 'r') as f:
        words = []
        senses = []
        senses_id = {}
        sense_count = 0
        for line in f.readlines():
            for token in line.split():
                split_token = token.split(sep)
                words.append(split_token[0])
                sense = 'a'
                if len(split_token) > 1:
                    sense = split_token[-1]
                senses.append(sense)
                if sense not in senses_id:
                    senses_id[sense] = sense_count
                    sense_count += 1
        answers = {}
        for w, s in zip(words, senses):
            if w not in answers:
                answers[w] = []
            answers[w].append(senses_id[s])
        return answers

def compute_metrics(answers, predictions):
    """
        Evaluates prediction against answers, and provides eval measures:
        fscore, vscore, ari (adjusted random index)
    """
    aris = []
    vscores = []
    one_sense_count = 0
    true_positive = 0
    false_negative = 0
    false_positive = 0
    for k in answers.keys():
        true = np.array(answers[k])
        pred = np.array(predictions[k])
        aris.append(adjusted_rand_score(true, pred))
        vscores.append(v_measure_score(true, pred))
        tp, fg, fp = compute_fscore(true, pred)
        true_positive += tp
        false_negative += fn
        false_positive += fp
        # if one_sense == True:
        #    one_sense_count += 1
        #print('%s: ari=%f, vscore=%f, fscore=%f' % (k, aris[-1], vscores[-1], fscores[-1]))
    #print('number of one-sense words in reference: %d' % one_sense_count)
    aris = np.array(aris)
    vscores = np.array(vscores)

    # calculate fscore
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    fscore = 2 * p * r / (p + r)

    print('mean ari: %f' % np.mean(aris))
    print('mean vscore: %f' % np.mean(vscores))
    #print('weighted vscore: %f' % np.sum(vscores * (weights / float(np.sum(weights)))))
    print('total fscore: %f' % fscore)
    #print('weighted fscore: %f' % np.sum(fscores * (weights / float(np.sum(weights)))))
    return np.mean(aris), np.mean(vscores), fscore
    #return np.mean(fscores)

def main(argv):
    """
        Modified from AdaGram's test-all.py to evaluate WSD in sense-annotated
        corpora inside a given directory, using a gold standard file, 
        which can be laborious to create.
        Similarly to AdaGram (http://proceedings.mlr.press/v51/bartunov16.pdf), 
        three metrics are used: V-Measure, F-score and ARI.
    """
    import getopt

    separator = "@"
    try:
        opts, args = getopt.getopt(argv, "ht:r:s:", ["testdir=", "reference=", "separator="])
    except getopt.GetoptError:
        print("Usage: ./evaluate_WSD.py -t <testdir> -r <reffile> [-s <separator>]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage: ./evaluate_WSD.py -t <testdir> -r <reffile> [-s <separator>]")
            sys.exit()
        elif opt in ("-t", "--testdir"):
            test_dir = arg
        elif opt in ("-r", "--reference"):
            ref_file = arg
        elif opt in ("-s", "--separator"):
            separator = arg

    ari_list = []
    vscore_list = []
    fscore_list = []
    eval_files = []
    true_answers = read_answers(ref_file, separator)
    for test_file in os.listdir(test_dir):
        print("Evaluating: {}".format(test_file))
        eval_files.append(test_file)
        predictions = read_answers(test_dir + "/" + test_file, separator)
        ari, vscore, fscore = compute_metrics(true_answers, predictions)
        ari_list.append(ari)
        vscore_list.append(vscore)
        fscore_list.append(fscore)
        print('\n')

    max_ari = max(ari_list)
    ari_indexes = [i for i, j in enumerate(ari_list) if j == max_ari]
    print("Best ari: {} in files {}\n".format(max_ari, [eval_files[i] for i in ari_indexes]))
    max_vscore = max(vscore_list)
    vscore_indexes = [i for i, j in enumerate(vscore_list) if j == max_vscore]
    print("Best vscore: {} in files {}\n".format(max_vscore, [eval_files[i] for i in vscore_indexes]))
    max_fscore = max(fscore_list)
    fscore_indexes = [i for i, j in enumerate(fscore_list) if j == max_fscore]
    print("Best fscore: {} in files {}\n".format(max_fscore, [eval_files[i] for i in fscore_indexes]))
    
if __name__ == '__main__':
    main(sys.argv[1:])
