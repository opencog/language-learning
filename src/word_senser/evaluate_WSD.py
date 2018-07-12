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
    one_sense = False
    # handling the case when there's only one sense for a word in "true"
    # if len(np.unique(true)) == 1:
    #     dumb, counts = np.unique(pred, return_counts=True)
    #     # precision and recall are the same in this case
    #     r = max(counts) / len(true)
    #     p = r
    #     one_sense = True
    # else:
    true_pairs = get_pairs(true)
    #print("true pairs {}".format(true_pairs))
    pred_pairs = get_pairs(pred)
    #print("pred pairs {}".format(pred_pairs))
    int_size = len(set(true_pairs).intersection(pred_pairs))
    # if there are not enough pairs to compare
    # if len(pred_pairs) == 0 or len(true_pairs) == 0:
    #     print("Returned ZERO")
    #     return 0
    p = int_size / float(len(pred_pairs))
    r = int_size / float(len(true_pairs))
    # in case both precision and recall are zero, return zero
    if (p + r) == 0:
        return 0
    return 2*p*r/float(p+r)

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
    #aris = []
    #vscores = []
    fscores = []
    #weights = []
    one_sense_count = 0
    for k in answers.keys():
        #print(k)
        true = np.array(answers[k])
        pred = np.array(predictions[k])
        #weights.append(pred.shape[0])
        #if len(np.unique(true)) > 1:
            #aris.append(adjusted_rand_score(true, pred))
        #vscores.append(v_measure_score(true, pred))
        fscore = compute_fscore(true, pred)
        fscores.append(fscore)
        # if one_sense == True:
        #    one_sense_count += 1
#        print('%s: ari=%f, vscore=%f, fscore=%f' % (k, aris[-1], vscores[-1], fscores[-1]))
    #aris = np.array(aris)
    #vscores = np.array(vscores)
    fscores = np.array(fscores)
    #weights = np.array(weights)
    print('number of one-sense words in reference: %d' % one_sense_count)
    #print('mean ari: %f' % np.mean(aris))
    #print('mean vscore: %f' % np.mean(vscores))
    #print('weighted vscore: %f' % np.sum(vscores * (weights / float(np.sum(weights)))))
    print('mean fscore: %f' % np.mean(fscores))
    #print('weighted fscore: %f' % np.sum(fscores * (weights / float(np.sum(weights)))))
    #return np.mean(aris),np.mean(vscores),np.mean(fscores)
    return np.mean(fscores)

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

    #ari_list = []
    #vscore_list = []
    fscore_list = []
    eval_files = []
    true_answers = read_answers(ref_file, separator)
    for test_file in os.listdir(test_dir):
        print("Evaluating: {}".format(test_file))
        eval_files.append(test_file)
        predictions = read_answers(test_dir + "/" + test_file, separator)
        #ari, vscore, fscore = compute_metrics(true_answers, predictions)
        fscore = compute_metrics(true_answers, predictions)
        #ari_list.append(ari)
        #vscore_list.append(vscore)
        fscore_list.append(fscore)
        print('\n')

    #max_ari = max(ari_list)
    #ari_indexes = [i for i, j in enumerate(ari_list) if j == max_ari]
    #print("Best ari: {} in files {}\n".format(max_ari, [eval_files[i] for i in ari_indexes]))
    #max_vscore = max(vscore_list)
    #vscore_indexes = [i for i, j in enumerate(vscore_list) if j == max_vscore]
    #print("Best vscore: {} in files {}\n".format(max_vscore, [eval_files[i] for i in vscore_indexes]))
    max_fscore = max(fscore_list)
    fscore_indexes = [i for i, j in enumerate(fscore_list) if j == max_fscore]
    print("Best fscore: {} in files {}\n".format(max_fscore, [eval_files[i] for i in fscore_indexes]))
    
if __name__ == '__main__':
    main(sys.argv[1:])
