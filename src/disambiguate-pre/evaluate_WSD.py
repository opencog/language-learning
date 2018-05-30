#!/usr/bin/env python

# ASuMa, May 2018
# Modified from AdaGram's test-all.py to evaluate WSD in annotated
# corpus produced with annotate_corpus.jl.
# Similarl to AdaGram (http://proceedings.mlr.press/v51/bartunov16.pdf), 
# three metrics are used: V-Measure, F-score and ARI.

import numpy as np
import sys
import os
import subprocess
import itertools
from sklearn.metrics import adjusted_rand_score,v_measure_score

def get_pairs(labels):
    result = []
    for label in np.unique(labels):
        ulabels = np.where(labels==label)[0]
        for p in itertools.combinations(ulabels, 2):
            result.append(p)
    return result

def compute_fscore(true, pred):
    print(true)
    true_pairs = get_pairs(true)
    pred_pairs = get_pairs(pred)
    print(true_pairs)
    print(pred_pairs)
    int_size = len(set(true_pairs).intersection(pred_pairs))
    p = int_size / float(len(pred_pairs))
    r = int_size / float(len(true_pairs))
    return 2*p*r/float(p+r)

def read_answers(filename, sep):
    with open(filename, 'r') as f:
        keys = []
        senses = []
        senses_id = {}
        sense_count = 0
        for line in f.readlines():
            for token in line.split():
                split_token = token.split(sep)
                keys.append(split_token[0])
                sense = 1
                if len(split_token) > 1:
                    sense = int(split_token[-1])
                senses.append(sense)
                if sense not in senses_id:
                    senses_id[sense] = sense_count
                    sense_count += 1
        answers = {}
        for k,s in zip(keys, senses):
            if k not in answers:
                answers[k] = []
            answers[k].append(senses_id[s])
        return answers

def compute_metrics(answers, predictions):
    aris = []
    vscores = []
    fscores = []
    weights = []
    for k in answers.keys():
        true = np.array(answers[k])
        pred = np.array(predictions[k])
        # skip if only one occurrence of a word in corpus
        if len(true) == 1:
            continue
        weights.append(pred.shape[0])
        if len(np.unique(true)) > 1:
            aris.append(adjusted_rand_score(true, pred))
        vscores.append(v_measure_score(true, pred))
        print(k)
        fscores.append(compute_fscore(true, pred))
#        print '%s: ari=%f, vscore=%f, fscore=%f' % (k, aris[-1], vscores[-1], fscores[-1])
    aris = np.array(aris)
    vscores = np.array(vscores)
    fscores = np.array(fscores)
    weights = np.array(weights)
    print 'number of one-sense words: %d' % (len(vscores) - len(aris))
    print 'mean ari: %f' % np.mean(aris)
    print 'mean vscore: %f' % np.mean(vscores)
    print 'weighted vscore: %f' % np.sum(vscores * (weights / float(np.sum(weights))))
    print 'mean fscore: %f' % np.mean(fscores)
    print 'weighted fscore: %f' % np.sum(fscores * (weights / float(np.sum(weights))))
    return np.mean(aris),np.mean(vscores)

def main(argv):
    import getopt

    separator = "@"
    try:
        opts, args = getopt.getopt(argv, "ht:r:s:", ["test=", "reference=", "separator="])
    except getopt.GetoptError:
        print("Usage: ./evaluate_WSD.py -t <testfile> -r <reffile> -s <separator>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage: ./evaluate_WSD.py -t <testfile> -r <reffile> -s <separator>")
            sys.exit()
        elif opt in ("-t", "--test"):
            test_file = arg
        elif opt in ("-r", "--reference"):
            ref_file = arg
        elif opt in ("-s", "--separator"):
            separator = arg

    true_answers = read_answers(ref_file, separator)
    predictions = read_answers(test_file, separator)
    compute_metrics(true_answers, predictions)
    print('\n')
    
if __name__ == '__main__':
    main(sys.argv[1:])