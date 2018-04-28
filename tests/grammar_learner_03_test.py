#!/usr/bin/env python3

import os, sys
import pytest
from src.grammar_learner.poc03 import learn_grammar
from src.utl.utl import UTC
from src.utl.read_files import check_dir

def setup_module():     #FIXME: check setup+function var definition
    module_path = os.path.abspath(os.path.join('.'))
    if module_path not in sys.path: sys.path.append(module_path)
    print('\n'+str(UTC()), ':: setup: module_path:', module_path)
    # Directory to read parse files:
    input_dir = module_path + '/data/POC_Turtle/MST_fixed_manually/'
    #-input_dir = module_path + '/data/POC_English_NoAmb/mst_fixed_manually/'
    base_dir  = module_path + '/tests/data/POC-Turtle/'  # baseline data files
        # base = base_dir + '...' -- below
    # Paths to store learned categories, dictionary Link Grammar file
    batch_dir = module_path + '/output/tests-' + str(UTC())[:10] + '/'
        # prj_dir = batch_dir + '...' -- below
    # Settings:
    parse_mode = 'given'        # 'given' (default) / 'explosive' (next)
    left_wall = 'LEFT-WALL'     # '','none' - don't use /
                                # 'string' - replace ###LEFT-WALL### with the string
    period = True               # use period in links learning: True/False
    # Vector space settings:
    context = 1                 # 1: connectors / 0: 'words' /
                                # 2,3...: disjuncts with limited number of links
    window = 'mst'              # 'mst' / reserved options for «explosive» parsing
    weighting = 'ppmi'          # 'ppmi' / future options
    group = True                # group items after link parsing, sum counts
    #+distance = False?
    word_space = 'vectors'      # 'vectors' / 'discrete' - no dimensionality reduction
    dim_max = 100               # max vector space dimensionality
    sv_min = 0.1                # minimal singular value (fraction of the max value)
    dim_reduction = 'svm'       # 'svm' / 'none' (discrete word_space, group)
    # Clustering settings:
    clustering = 'kmeans'       # 'kmeans' / 'group'~'identical_entries' / future options
    cluster_range = (2,48,1)    # min, max, step
    cluster_criteria = 'silhouette'
    cluster_level = 0.9         # level = 0, 1, 0.-0.99..: 0 - max number of clusters
    # Generalization settings:
    generalization = 'off'      # 'off' / future options: 'cosine', ...
    merge = 0.8                 # merge clusters with similarity > this 'merge' criteria
    aggregate = 0.2             # agglomerate clusters with similarity > this criteria
    # Grammar rules:
    grammar_rules = 1           # 1: 'connectors' / 2: 'disjuncts' / 0: 'words' (TODO?)
    verbose='mid'   # display intermediate results: 'none', 'min', 'mid', 'max'
    #-print('Setup')

def test_turtle_drk():  # "Connectors-DRK-disjuncts"
    print(UTC(), ':: test_turtle_drk(): «Connectors-DRK-Disjuncts»')
    module_path = os.path.abspath(os.path.join('.'))
    if module_path not in sys.path: sys.path.append(module_path)
    print('module_path:', module_path)
    input_dir = module_path + '/data/POC-Turtle/MST_fixed_manually/'
    base  = module_path + '/tests/data/POC-Turtle/turtle_cDRKd_LW+dot+_2018-04-25_0008.4.0.dict'
    batch_dir = module_path + '/output/tests-' + str(UTC())[:10] + '/'
    prj_dir = batch_dir + 'connectors-DRK-disjuncts_LW+dot+/'
    if check_dir(prj_dir, create=True, verbose='max'):
        cat_path = prj_dir  # Path to store learned categories
        dict_path = prj_dir # Path to store learned dictionary Link Grammar file
        tmpath = prj_dir    # Save temporary files to the project directory
        #-tmpath = module_path + '/tmp/'
    # Settings:
    parse_mode = 'given'        # 'given' (default) / 'explosive' (next)
    left_wall = 'LEFT-WALL'     # '','none' - don't use / # 'string' - replace ###LEFT-WALL### with the string
    period = True               # use period in links learning: True/False
    context = 1                 # 1: connectors / 0: 'words' / 2...: disjuncts with limited number of links
    window = 'mst'              # 'mst' / reserved options for «explosive» parsing
    weighting = 'ppmi'          # 'ppmi' / future options
    group = True                # group items after link parsing, sum counts
    #+distance = False?
    word_space = 'vectors'      # 'vectors' / 'discrete' - no dimensionality reduction
    dim_max = 100               # max vector space dimensionality
    sv_min = 0.1                # minimal singular value (fraction of the max value)
    dim_reduction = 'svm'       # 'svm' / 'none' (discrete word_space, group)
    clustering = 'kmeans'       # 'kmeans' / 'group'~'identical_entries' / future options
    cluster_range = (2,48,1)    # min, max, step
    cluster_criteria = 'silhouette'
    cluster_level = 0.9         # level = 0, 1, 0.-0.99..: 0 - max number of clusters
    generalization = 'off'      # 'off' / future options: 'cosine', ...
    merge = 0.8                 # merge clusters with similarity > this 'merge' criteria
    aggregate = 0.2             # agglomerate clusters with similarity > this criteria
    grammar_rules = 2           # 1: 'connectors' / 2: 'disjuncts' / 0: 'words' (TODO?)
    verbose='min'   # display intermediate results: 'none', 'min', 'mid', 'max'

    rules = learn_grammar(input_dir, cat_path, dict_path, tmpath, verbose, \
        parse_mode, left_wall, period, context, window, weighting, group, \
        word_space, dim_max, sv_min, dim_reduction, \
        clustering, cluster_range, cluster_criteria, cluster_level,
        generalization, merge, aggregate, grammar_rules)
    print(rules.split('\n')[-1][2:], '\n')
    rule_list = [line for line in rules.split('\n') if line[0:1] in ['"', '(']]
    with open(base, 'r') as f: lst = f.read().splitlines()
    base_list = [line for line in lst if line[0:1] in ['"', '(']]
    if len(rule_list) == len(base_list):
        if verbose == 'debug':
            print('\nTest results vs baseline:')
            for i,rule in enumerate(base_list):
                print(rule_list[i])
                print(rule)
        assert rule_list == base_list
    else: assert len(rule_list) == len(base_list)

def test_turtle_ile():  # "Disjuncts-ILE-disjuncts"
    # context = 2
    # word_space = 'discrete'
    # dim_reduction = 'none'
    # clustering = 'group'
    # grammar_rules = 2
    print(UTC(), ':: test_turtle_ile(): «Disjuncts-ILE-Disjuncts»')
    module_path = os.path.abspath(os.path.join('.'))
    if module_path not in sys.path: sys.path.append(module_path)
    #-print('module_path:', module_path)
    input_dir = module_path + '/data/POC-Turtle/MST_fixed_manually/'
    base  = module_path + '/tests/data/POC-Turtle/turtle_dILEd_LW+dot+_2018-04-25_0008.4.0.dict'
    batch_dir = module_path + '/output/tests-' + str(UTC())[:10] + '/'
    prj_dir = batch_dir + 'disjuncts-ILE-disjuncts_LW+dot+/'
    if check_dir(prj_dir, create=True, verbose='max'):
        cat_path = prj_dir  # Path to store learned categories
        dict_path = prj_dir # Path to store learned dictionary Link Grammar file
        tmpath = prj_dir    # Save temporary files to the project directory
        #-tmpath = module_path + '/tmp/'
    # Settings:
    parse_mode = 'given'        # 'given' (default) / 'explosive' (next)
    left_wall = 'LEFT-WALL'     # '','none' - don't use / # 'string' - replace ###LEFT-WALL### with the string
    period = True               # use period in links learning: True/False
    context = 2                 # 1: connectors / 0: 'words' / 2...: disjuncts with limited number of links
    window = 'mst'              # 'mst' / reserved options for «explosive» parsing
    weighting = 'ppmi'          # 'ppmi' / future options
    group = True                # group items after link parsing, sum counts
    #+distance = False?
    word_space = 'discrete'     # 'vectors' / 'discrete' - no dimensionality reduction
    dim_max = 100               # max vector space dimensionality
    sv_min = 0.1                # minimal singular value (fraction of the max value)
    dim_reduction = 'none'      # 'svm' / 'none' (discrete word_space, group)
    clustering = 'group'        # 'kmeans' / 'group'~'identical_entries' / future options
    cluster_range = (2,48,1)    # min, max, step
    cluster_criteria = 'silhouette'
    cluster_level = 0.9         # level = 0, 1, 0.-0.99..: 0 - max number of clusters
    generalization = 'off'      # 'off' / future options: 'cosine', ...
    merge = 0.8                 # merge clusters with similarity > this 'merge' criteria
    aggregate = 0.2             # agglomerate clusters with similarity > this criteria
    grammar_rules = 2           # 1: 'connectors' / 2: 'disjuncts' / 0: 'words' (TODO?)
    verbose='min'   # display intermediate results: 'none', 'min', 'mid', 'max'

    rules = learn_grammar(input_dir, cat_path, dict_path, tmpath, verbose, \
        parse_mode, left_wall, period, context, window, weighting, group, \
        word_space, dim_max, sv_min, dim_reduction, \
        clustering, cluster_range, cluster_criteria, cluster_level,
        generalization, merge, aggregate, grammar_rules)
    print(rules.split('\n')[-1][2:], '\n')
    rule_list = [line for line in rules.split('\n') if line[0:1] in ['"', '(']]
    #-for x in rule_list: print(x)
    with open(base, 'r') as f: lst = f.read().splitlines()
    base_list = [line for line in lst if line[0:1] in ['"', '(']]
    #-for x in base_list: print(x)
    if len(rule_list) == len(base_list):
        if verbose == 'debug':
            print('\nTest results vs baseline:')
            for i,rule in enumerate(base_list):
                print(rule_list[i])
                print(rule)
        assert rule_list == base_list
    else: assert len(rule_list) == len(base_list)
