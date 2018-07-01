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
    result = []
    for label in np.unique(labels):
        ulabels = np.where(labels==label)[0]
        for p in itertools.combinations(ulabels, 2):
            result.append(p)
    return result

def compute_fscore(true, pred):
    true_pairs = get_pairs(true)
    pred_pairs = get_pairs(pred)
    int_size = len(set(true_pairs).intersection(pred_pairs))
    # if there are just not enough pairs to compare
    if len(pred_pairs) == 0 or len(true_pairs) == 0:
        return 0
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
        weights.append(pred.shape[0])
        if len(np.unique(true)) > 1:
            aris.append(adjusted_rand_score(true, pred))
        vscores.append(v_measure_score(true, pred))
        fscores.append(compute_fscore(true, pred))
#        print('%s: ari=%f, vscore=%f, fscore=%f' % (k, aris[-1], vscores[-1], fscores[-1]))
    aris = np.array(aris)
    vscores = np.array(vscores)
    fscores = np.array(fscores)
    weights = np.array(weights)
    print('number of one-sense words in reference: %d' % (len(vscores) - len(aris)))
    print('mean ari: %f' % np.mean(aris))
    print('mean vscore: %f' % np.mean(vscores))
    #print('weighted vscore: %f' % np.sum(vscores * (weights / float(np.sum(weights)))))
    print('mean fscore: %f' % np.mean(fscores))
    #print('weighted fscore: %f' % np.sum(fscores * (weights / float(np.sum(weights)))))
    return np.mean(aris),np.mean(vscores),np.mean(fscores)

def main(argv):
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
        predictions = read_answers(test_dir + test_file, separator)
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
