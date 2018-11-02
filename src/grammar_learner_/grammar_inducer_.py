# language-learning/src/grammar_learner_/grammar_inducer_.py    shadow  # 81025
from copy import deepcopy
from collections import Counter
from typing import List, Tuple
from .category_learner_ import cats2list
from ull.grammar_learner.utl import UTC


def induce_grammar(categories, **kwargs):  # 81025
    # categories == {'cluster': [], 'words': [], ...}
    def kwa(v, k):
        return kwargs[k] if k in kwargs else v

    max_disjuncts = kwa(1000, 'max_disjuncts')  # 81025
    verbose = kwa('none', 'verbose')

    # verbose = 'debug'  # 81031 FIXME:DEL

    if verbose in ['max', 'debug']:
        print(UTC(), ':: induce_grammar: categories.keys():', categories.keys())

    rules = deepcopy(categories)
    dj_counts = Counter()  # 81025

    clusters = [i for i, x in enumerate(rules['cluster']) if i > 0 and x is not None]
    word_clusters = dict()
    for i in clusters:
        for word in rules['words'][i]:
            word_clusters[word] = i

    if verbose in ['max', 'debug']:
        print('induce_grammar: rules.keys():', rules.keys())
        print('induce_grammar: clusters:', clusters)
        # print('induce_grammar: word_clusters:', word_clusters)
        print('induce_grammar: rules ~ categories:')

    for cluster in clusters:
        djs = []
        for i, rule in enumerate(categories['disjuncts'][cluster]):  # 81025
            if type(rule) is str:  # 'a- & was-' ⇒ (-9,-26)    reverse   81012
                x = rule.split()
                lefts = []
                rights = []
                for y in x:
                    if (y not in ['&', ' ', '']) and (y[:-1] in word_clusters):
                        if y[-1] == '+':
                            rights.append(word_clusters[y[:-1]])
                        elif y[-1] == '-':
                            lefts.append(-1 * word_clusters[y[:-1]])
                        else:
                            print('no sign?', y, 'in', x)  # TODO:ERROR?
                lefts.reverse()  # 81012
                dj = lefts + rights
                if len(dj) > 0:
                    djs.append(tuple(dj))
                    dj_counts[tuple(dj)] += categories['dj_counts'][cluster][i]
                if verbose == 'debug':
                    print(f'induce_grammar_: cluster {cluster}: {rule} ⇒ {tuple(dj)}')
            # TODO? +elif type(rule) is tuple? connectors - tuples?
        rules['disjuncts'][cluster] = set(djs)

        if verbose in ['max', 'debug']:
            print('induce_grammar: rules["disjuncts"][' + str(cluster) + ']', len(rules['disjuncts'][cluster]),
                  'rules,', len(dj_counts), 'total unique disjunts')

    # 81025 add only top (filtered) disjuncts:
    top_djs = set([x[0] for x in dj_counts.most_common(max_disjuncts)])

    if verbose in ['debug']:
        print(max_disjuncts, 'top_djs:', top_djs)
        for cluster in clusters:
            rules['disjuncts'][cluster] = top_djs & rules['disjuncts'][cluster]
        print('\nrules:')
        nr = 0
        for cluster in clusters:
            print('\n', cluster, len(rules['disjuncts'][cluster]))  #, 'rules:'),
            # rules['disjuncts'][cluster])
            nr += len(rules['disjuncts'][cluster])
        print('Total:', nr)

    # rules['djs'] = deepcopy(rules['disjuncts'])  # no need: conversion in g12n
    # TOD0?: check jaccard with tuples else replace with numbers?

    return rules, {'learned_rules': len([x for i, x in enumerate(rules['parent']) if x == 0 and i > 0]), \
                   'total_clusters': len(rules['cluster']) - 1}

# Notes:

# 80802 poc05.py restructured: induce_grammar ⇒ grammar_inducer.py v~80625
