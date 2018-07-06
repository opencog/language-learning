#!/usr/bin/env python3
'''
Grammar Learner POC.0.5 tests #80706: pytest⇒unittest, new Link Grammar Tester
Run test:
$ cd language-learning
$ source activate ull4
$ python tests/test_grammar_learner.py
'''
#from pathlib import Path
#print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

import os, sys
import unittest
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
from src.utl.utl import UTC
from src.utl.read_files import check_dir
from src.grammar_learner.poc05 import learn_grammar

class TestGrammarLearner(unittest.TestCase):

    def setUp(self):    #FIXME: should run before every test, but would not?!
        #-import os, sys
        # Paths #FIXME: don't run?
        #module_path = os.path.abspath(os.path.join('..'))
        #if module_path not in sys.path:
        #    sys.path.append(module_path)
        # Imports - moved up:  #FIXME: don't run here?
        #-from src.grammar_learner.poc05 import learn_grammar
        #-from src.utl.utl import UTC
        src_path = module_path + '/src'
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.append(src_path)
        # Don't need link grammar paths with new (June 2018) Grammar Tester (?)
        #-lg_path = '/home/oleg/miniconda3/envs/ull4/lib/python3.6/site-packages/linkgrammar'
        #-if os.path.exists(lg_path) and lg_path not in sys.path:
        #-    sys.path.append(lg_path)
        #-link_grammar_path = module_path + '/src/link_grammar'
        #-if os.path.exists(link_grammar_path) and link_grammar_path not in sys.path:
        #-    sys.path.append(link_grammar_path)
        input_parses = module_path + '/tests/data/POC-Turtle/MST_fixed_manually/'
        batch_dir = module_path + '/output/Test_Grammar_Learner_' + str(UTC())[:10] + '/'
        # Grammar Learner 0.5 parameters:
        # input_parses, output_categories, output_grammar, **kwargs
        kwargs = {  # defaults  #FIXME: don't pass to tests (should?)
            'parse_mode'    :   'given'     ,   # 'given' (default) / 'explosive' (next)
            'left_wall'     :   'LEFT-WALL' ,   # '','none' - don't use / 'LEFT-WALL' - replace ###LEFT-WALL###
            'period'        :   True        ,   # use period in links learning: True/False
            'context'       :   2           ,   # 1: connectors / 2,3...: disjuncts
            'window'        :   'mst'       ,   # 'mst' / reserved options for «explosive» parsing
            'weighting'     :   'ppmi'      ,   # 'ppmi' / future options
            'group'         :   True        ,   # group items after link parsing
            'distance'      :   False       ,   # reserved options for «explosive» parsing
            'word_space'    :   'discrete'  ,   # 'vectors' / 'discrete' - no dimensionality reduction
            'dim_max'       :   100         ,   # max vector space dimensionality
            'sv_min'        :   0.1         ,   # minimal singular value (fraction of the max value)
            'dim_reduction' :   'none'      ,   # 'svm' / 'none' (discrete word_space, group)
            'clustering'    :   'group'     ,   # 'kmeans' / 'group'~'identical_entries' / future options
            'cluster_range' :   (2,48,1)    ,   # min, max, step
            'cluster_criteria': 'silhouette',   # optimal clustering criteria
            'cluster_level' :   0.9         ,   # level = 0, 1, 0.-0.99..: 0 - max number of clusters
            'categories_generalization': 'off', # 'off' / 'cosine' - cosine similarity, 'jaccard'
            'categories_merge'      :   0.8 ,   # merge categories with similarity > this 'merge' criteria
            'categories_aggregation':   0.2 ,   # aggregate categories with similarity > this criteria
            'grammar_rules' :   2           ,   # 1: 'connectors' / 2 - 'disjuncts' / 0 - 'words' (TODO?)
            'rules_generalization'  :  'off',   # 'off' / 'cosine' - cosine similarity, 'jaccard'
            'rules_merge'           :   0.8 ,   # merge rules with similarity > this 'merge' criteria
            'rules_aggregation'     :   0.2 ,   # aggregate rules similarity > this criteria
            'tmpath'        :   module_path + '/tmp/',
            'verbose': 'min', # display intermediate results: 'none', 'min', 'mid', 'max'
            # Additional (optional) parameters for parse_metrics (_abiity & _quality):
            'test_corpus'   :   module_path + '/data/POC-Turtle/poc-turtle-corpus.txt',
            'reference_path':   module_path + '/data/POC-Turtle/poc-turtle-parses-expected.txt',
            'template_path' :   'poc-turtle',  #FIXME: changed in June 2018 Grammar Tester
            'linkage_limit' :   1
        }
        pass

    #Legacy ~POC.0.3 test (still runs OK with ImportWarning)
    def test_turtle_diled(self):
        corpus = 'POC-Turtle'
        dataset = 'MST_fixed_manually'
        input_parses = module_path + '/tests/data/POC-Turtle/MST_fixed_manually/'
        base  = module_path + '/tests/data/POC-Turtle/' + \
            '/2018-04-25/turtle_dILEd_LW+dot+_2018-04-25_0008.4.0.dict'
        batch_dir = module_path + '/output/Test_Grammar_Learner_' + str(UTC())[:10] + '/'
        prj_dir = batch_dir + 'Turtle_dILEd_LW_and_period/'
        if check_dir(prj_dir, create=True, verbose='max'):
            output_categories = prj_dir
            output_grammar = prj_dir
        kwargs = {
            'left_wall'     :   'LEFT-WALL' ,
            'period'        :   True        ,
            'context'       :   2           ,
            'word_space'    :   'discrete'  ,
            'dim_reduction' :   'none'      ,
            'clustering'    :   'group'     ,
            'grammar_rules' :   2           ,
            'categories_generalization' :   'off' ,
            'rules_generalization'      :   'off' ,
            'tmpath'        :   module_path + '/tmp/',
            'verbose'       :   'min'
        }
        response = learn_grammar(input_parses, output_categories, output_grammar, **kwargs)
        with open(response['grammar_file'], 'r') as f:
            rules = f.read().splitlines()
        rule_list = [line for line in rules if line[0:1] in ['"', '(']]
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


    def test_turtle_no_generalization(self):
        base  = module_path + '/tests/data/POC-Turtle/' + \
            'no_generalization/poc-turtle_8C_2018-06-08_0004.4.0.dict'
        input_parses = module_path + '/tests/data/POC-Turtle/MST_fixed_manually/'
        batch_dir = module_path + '/output/Test_Grammar_Learner_' + str(UTC())[:10] + '/'
        prj_dir = batch_dir + 'no_generalization/'
        if check_dir(prj_dir, create=True, verbose='max'):
            outpath = prj_dir
        kwargs = {
            'left_wall'     :   'LEFT-WALL' ,
            'period'        :   True        ,
            'context'       :   2           ,
            'word_space'    :   'discrete'  ,
            'dim_reduction' :   'none'      ,
            'clustering'    :   'group'     ,
            'grammar_rules' :   2           ,
            'categories_generalization' :   'off' ,
            'rules_generalization'      :   'off' ,
            'tmpath'        :   module_path + '/tmp/',
            'verbose'       :   'none'
        }
        response = learn_grammar(input_parses, outpath, outpath, **kwargs)
        with open(response['grammar_file'], 'r') as f:
            rules = f.read().splitlines()
        rule_list = [line for line in rules if line[0:1] in ['"', '(']]
        with open(base, 'r') as f: lst = f.read().splitlines()
        base_list = [line for line in lst if line[0:1] in ['"', '(']]
        if len(rule_list) == len(base_list):
            assert rule_list == base_list
        else: assert len(rule_list) == len(base_list)


    def test_turtle_generalize_categories(self):
        base  = module_path + '/tests/data/POC-Turtle/' + \
            'generalized_categories/dict_6C_2018-07-06_0005.4.0.dict'
            #'generalized_categories/poc-turtle_6C_2018-06-08_0004.4.0.dict'
        input_parses = module_path + '/tests/data/POC-Turtle/MST_fixed_manually/'
        batch_dir = module_path + '/output/Test_Grammar_Learner_' + str(UTC())[:10] + '/'
        prj_dir = batch_dir + 'generalized_categories/'
        if check_dir(prj_dir, create=True, verbose='max'):
            outpath = prj_dir
        kwargs = {
            'left_wall'     :   'LEFT-WALL' ,
            'period'        :   True        ,
            'context'       :   2           ,
            'word_space'    :   'discrete'  ,
            'dim_reduction' :   'none'      ,
            'clustering'    :   'group'     ,
            'grammar_rules' :   2           ,
            'categories_generalization' :   'jaccard',
            'rules_generalization'      :   'off'    ,
            'tmpath'        :   module_path + '/tmp/',
            'verbose'       :   'none'
        }
        response = learn_grammar(input_parses, outpath, outpath, **kwargs)
        with open(response['grammar_file'], 'r') as f:
            rules = f.read().splitlines()
        rule_list = [line for line in rules if line[0:1] in ['"', '(']]
        with open(base, 'r') as f:
            lst = f.read().splitlines()
        base_list = [line for line in lst if line[0:1] in ['"', '(']]
        if len(rule_list) == len(base_list):
            assert rule_list == base_list
        else: assert len(rule_list) == len(base_list)


    def test_turtle_generalize_rules(self):
        base  = module_path + '/tests/data/POC-Turtle/' + \
            'generalized_rules/dict_6C_2018-07-06_0005.4.0.dict'
            #'generalized_rules/poc-turtle_6C_2018-06-08_0004.4.0.dict'
        input_parses = module_path + '/tests/data/POC-Turtle/MST_fixed_manually/'
        batch_dir = module_path + '/output/Test_Grammar_Learner_' + str(UTC())[:10] + '/'
        prj_dir = batch_dir + 'generalized_rules/'
        if check_dir(prj_dir, create=True, verbose='max'):
            outpath = prj_dir
        kwargs = {
            'left_wall'     :   'LEFT-WALL' ,
            'period'        :   True        ,
            'context'       :   2           ,
            'word_space'    :   'discrete'  ,
            'dim_reduction' :   'none'      ,
            'clustering'    :   'group'     ,
            'grammar_rules' :   2           ,
            'categories_generalization' :   'off'    ,
            'rules_generalization'      :   'jaccard',
            'tmpath'        :   module_path + '/tmp/',
            'verbose'       :   'none'
        }
        response = learn_grammar(input_parses, outpath, outpath, **kwargs)
        with open(response['grammar_file'], 'r') as f:
            rules = f.read().splitlines()
        rule_list = [line for line in rules if line[0:1] in ['"', '(']]
        with open(base, 'r') as f: lst = f.read().splitlines()
        base_list = [line for line in lst if line[0:1] in ['"', '(']]
        if len(rule_list) == len(base_list):
            assert rule_list == base_list
        else: assert len(rule_list) == len(base_list)


    def test_turtle_generalize_both(self):
        base  = module_path + '/tests/data/POC-Turtle/' + \
            'generalized_categories_and_rules/dict_6C_2018-07-06_0005.4.0.dict'
            #'generalized_categories_and_rules/poc-turtle_6C_2018-06-08_0004.4.0.dict'
        input_parses = module_path + '/tests/data/POC-Turtle/MST_fixed_manually/'
        batch_dir = module_path + '/output/Test_Grammar_Learner_' + str(UTC())[:10] + '/'
        prj_dir = batch_dir + 'generalized_categories_and_rules/'
        if check_dir(prj_dir, create=True, verbose='max'):
            outpath = prj_dir
        kwargs = {
            'left_wall'     :   'LEFT-WALL' ,
            'period'        :   True        ,
            'context'       :   2           ,
            'word_space'    :   'discrete'  ,
            'dim_reduction' :   'none'      ,
            'clustering'    :   'group'     ,
            'grammar_rules' :   2           ,
            'categories_generalization' :   'jaccard',
            'rules_generalization'      :   'jaccard',
            'tmpath'        :   module_path + '/tmp/',
            'verbose'       :   'none'
        }
        response = learn_grammar(input_parses, outpath, outpath, **kwargs)
        with open(response['grammar_file'], 'r') as f:
            rules = f.read().splitlines()
        rule_list = [line for line in rules if line[0:1] in ['"', '(']]
        with open(base, 'r') as f: lst = f.read().splitlines()
        base_list = [line for line in lst if line[0:1] in ['"', '(']]
        if len(rule_list) == len(base_list):
            assert rule_list == base_list
        else: assert len(rule_list) == len(base_list)


if __name__ == '__main__':
    unittest.main()
