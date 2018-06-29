#!/usr/bin/env python3

import os, sys
import pytest
from src.grammar_learner.poc05 import learn_grammar
from src.utl.utl import UTC
from src.utl.read_files import check_dir

def setup_module():     #FIXME: check setup+function var definition     #80629
    module_path = os.path.abspath(os.path.join('.'))
    if module_path not in sys.path:
        sys.path.append(module_path)
    src_path = module_path + '/src'
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.append(src_path)
    lg_path = '/home/oleg/miniconda3/envs/ull4/lib/python3.6/site-packages/linkgrammar'
    if os.path.exists(lg_path) and lg_path not in sys.path:
        sys.path.append(lg_path)
    link_grammar_path = module_path + '/src/link_grammar'
    if os.path.exists(link_grammar_path) and link_grammar_path not in sys.path:
        sys.path.append(link_grammar_path)

def test_turtle_ile():  # "Disjuncts-ILE-disjuncts"                     #80629
    print(UTC(), ':: test_turtle_ile(): «Disjuncts-ILE-Disjuncts»')
    module_path = os.path.abspath(os.path.join('.'))
    if module_path not in sys.path:
        sys.path.append(module_path)
    src_path = module_path + '/src'
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.append(src_path)
    lg_path = '/home/oleg/miniconda3/envs/ull4/lib/python3.6/site-packages/linkgrammar'
    if os.path.exists(lg_path) and lg_path not in sys.path:
        sys.path.append(lg_path)
    link_grammar_path = module_path + '/src/link_grammar'
    if os.path.exists(link_grammar_path) and link_grammar_path not in sys.path:
        sys.path.append(link_grammar_path)

    input_parses = module_path + '/data/POC-Turtle/MST_fixed_manually/'
    base  = module_path + \
        '/tests/data/POC-Turtle/turtle_dILEd_LW+dot+_2018-04-25_0008.4.0.dict'
    batch_dir = module_path + '/output/tests-' + str(UTC())[:10] + '/'
    prj_dir = batch_dir + 'disjuncts-ILE-disjuncts_LW+dot+/'
    if check_dir(prj_dir, create=True, verbose='max'):
        output_categories = prj_dir
        output_grammar = prj_dir
        tmpath = module_path + '/tmp/'
    corpus = 'POC-Turtle'
    dataset = 'MST_fixed_manually'
    kwargs = {
        'left_wall'     :   'LEFT-WALL'        ,
        'period'        :   True        ,
        'context'       :   2           ,
        'word_space'    :   'discrete'  ,
        'dim_reduction' :   'none'      ,
        'clustering'    :   'group'     ,
        'categories_generalization' :   'off' ,
        'categories_merge'          :   0.8       ,
        'categories_aggregation'    :   0.5       ,
        'grammar_rules'             :   2         ,
        'rules_generalization'      :   'off'     ,
        'rules_merge'               :   0.8       ,
        'rules_aggregation'         :   0.2       ,
        'verbose'       :   'max'   ,
        'test_corpus'   :   module_path + \
            '/data/POC-Turtle/poc-turtle-corpus.txt',
        'reference_path':   module_path + \
            '/data/POC-Turtle/poc-turtle-parses-expected.txt',
        'template_path' :   'poc-turtle',
        'linkage_limit' :   1
    }
    if kwargs['verbose'] in ['max','debug']:
        print('Paths:')
        for x in sys.path: print(x)

    response = learn_grammar(input_parses, output_categories, output_grammar, **kwargs)
    with open(response['grammar_file'], 'r') as f: rules = f.read().splitlines()
    rule_list = [line for line in rules if line[0:1] in ['"', '(']]
    for x in rule_list: print(x)
    with open(base, 'r') as f: lst = f.read().splitlines()
    base_list = [line for line in lst if line[0:1] in ['"', '(']]
    if len(rule_list) == len(base_list):
        if kwargs['verbose'] == 'debug':
            print('\nTest results vs baseline:')
            for i,rule in enumerate(base_list):
                print(rule_list[i])
                print(rule)
        assert rule_list == base_list
    else: assert len(rule_list) == len(base_list)
