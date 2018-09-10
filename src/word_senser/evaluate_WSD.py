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
        Returns pure f-score and a flag indicating if word was
        over-disambiguated (1) or not (0).
    """
    unique_true = np.unique(true)
    unique_pred = np.unique(pred)

    # if word should not be disambiguated
    if len(unique_true) == 1:
        if len(unique_pred) == 1: # not disambiguated
            return None, 0 # return a value that will be filtered later
        else: # punish wrongly disambiguated words
            over_sensed = 1
            return None, 1
    else: # if word should be disambiguated
        # if len(unique_pred) == 1: # not disambiguated
        #     p = 0
        #     r = 0
        # else: # calculate precision and recall
        true_pairs = get_pairs(true)
        pred_pairs = get_pairs(pred)
        int_size = len(set(true_pairs).intersection(pred_pairs))
        p = int_size / float(len(pred_pairs))# + 1e-5 # add eps to avoid div by zero
        r = int_size / float(len(true_pairs))# + 1e-5 

    # return fscore
    return 2 * p * r / (p + r), 0

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
    fscores = []
    one_sense_count = 0
    cnt_over_disamb = 0
    for k in answers.keys():
        true = np.array(answers[k])
        pred = np.array(predictions[k])
        aris.append(adjusted_rand_score(true, pred))
        vscores.append(v_measure_score(true, pred))
        fscore, over_disamb = compute_fscore(true, pred)
        cnt_over_disamb += over_disamb
        fscores.append(fscore)
    aris = np.array(aris)
    vscores = np.array(vscores)
    fscores[:] = (value for value in fscores if value != None) # remove None's
    fscores = np.array(fscores)
    mean_fscore = np.mean(fscores)
    mixed_score = (mean_fscore + (1 - float(cnt_over_disamb) / len(answers))) / 2
    print('mean ari: %f' % np.mean(aris))
    print('mean vscore: %f' % np.mean(vscores))
    print('mean fscore: %f' % mean_fscore) # pure f-score
    print('over disambiguated count: %d' % cnt_over_disamb) # over disambuated
    print('WSD score: %f' % mixed_score) # mixed score
    return np.mean(aris), np.mean(vscores), mean_fscore, mixed_score

def main(argv):
    """
        Modified from AdaGram's test-all.py to evaluate WSD in sense-annotated
        corpora inside a given directory, using a gold standard file, 
        which can be laborious to create.
        Similarly to AdaGram (http://proceedings.mlr.press/v51/bartunov16.pdf), 
        three metrics are used: V-Measure, F-score and ARI.
    """
    import getopt
    from random import randint

    separator = "@"
    rand_repeats = 10
    random_benchmark = False
    try:
        opts, args = getopt.getopt(argv, "ht:r:s:z", ["testdir=", "reference=", "separator=", "random"])
    except getopt.GetoptError:
        print("Usage: ./evaluate_WSD.py -t <testdir> -r <reffile> [-s <separator>] [-z]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("Usage: ./evaluate_WSD.py -t <testdir> -r <reffile> [-s <separator>] [-z]")
            sys.exit()
        elif opt in ("-t", "--testdir"):
            test_dir = arg
        elif opt in ("-r", "--reference"):
            ref_file = arg
        elif opt in ("-s", "--separator"):
            separator = arg
        elif opt in ("-z", "--random"):
            random_benchmark = True

    ari_list = []
    vscore_list = []
    fscore_list = []
    wsd_score_list = []
    eval_files = []
    true_answers = read_answers(ref_file, separator)

    # compare reference to random benchmark
    if random_benchmark:
        fscore = 0
        for repeat in range(rand_repeats):
            predictions = {}
            for word in true_answers.keys():
                num_senses = len(set(true_answers[word]))
                predictions[word] = [randint(1, num_senses) for i in range(len(true_answers[word]))]
            scores = compute_metrics(true_answers, predictions)
            fscore += scores[2]
        print("\nAverage fscore after {} random benchmarks: {}\n".format(rand_repeats, fscore / rand_repeats))
    # compare reference to test
    else:
        for test_file in os.listdir(test_dir):
            print("Evaluating: {}".format(test_file))
            eval_files.append(test_file)
            predictions = read_answers(test_dir + "/" + test_file, separator)
            ari, vscore, fscore, punished_fscore = compute_metrics(true_answers, predictions)
            ari_list.append(ari)
            vscore_list.append(vscore)
            fscore_list.append(fscore)
            wsd_score_list.append(punished_fscore)
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
        max_wsd_score = max(wsd_score_list)
        wsd_score_indexes = [i for i, j in enumerate(wsd_score_list) if j == max_wsd_score]
        print("Best WSD score: {} in files {}\n".format(max_wsd_score, [eval_files[i] for i in wsd_score_indexes]))
    
if __name__ == '__main__':
    main(sys.argv[1:])
