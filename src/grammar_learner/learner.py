#language-learning/src/learner.py                                   #   80829
import os
from copy import deepcopy
import pickle, pandas as pd  # , collections
from shutil import copy2 as copy
from IPython.display import display
from collections import OrderedDict

from .widgets import html_table
from .utl import UTC
from .read_files import check_dir, check_mst_files
from .pparser import files2links
from .category_learner import learn_categories, add_disjuncts, cats2list
# from ..grammar_learner_.grammar_inducer_ import induce_grammar   # tested 81029-31
from .grammar_inducer import induce_grammar
from .generalization import generalize_categories, generalize_rules
from .write_files import list2file, save_link_grammar, save_cat_tree

__all__ = ['learn_grammar']

#-def learn_grammar(input_parses, output_categories, output_grammar, **kwargs):
#-def learn_grammar(input_parses, output_categories, output_grammar, \
#-                  output_statistics='', temp_dir='', **kwargs):     #80810
    # input_parses - dir with .txt files
    # output_categories - path/file.ext / dir ⇒ auto file name
    # output_grammar    - path/file.ext / dir ⇒ auto file name
    # output_statistics - path/file.ext / dir ⇒ auto file name, '' ⇒ = output_grammar
def learn_grammar(**kwargs):                                        #   80929
    log = OrderedDict({'start': str(UTC()), 'learn_grammar': 'v.0.6.80929'})
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    # 80929 parameters (input and output paths) ⇒ kwargs:
    input_parses = kwargs['input_parses']
    output_grammar = kwargs['output_grammar']
    output_categories = kwa('', 'output_categories')
    output_statistics = kwa('', 'output_statistics')
    temp_dir = kwa('', 'temp_dir')
    if os.path.isdir(output_grammar):
        prj_dir = output_grammar
    else:  prj_dir = os.path.dirname(output_grammar)
    log.update({'project_directory': prj_dir})
    if output_categories == '':
        output_categories = prj_dir
    if output_statistics != '':                     # TODO: check path: filename/dir?
        corpus_stats_file = output_statistics
    else: corpus_stats_file = prj_dir+'/corpus_stats.txt'
    if temp_dir != '':
        if os.path.isdir(temp_dir):
            kwargs['tmpath'] = temp_dir

    parse_mode      = kwa('lower',  'parse_mode')
    left_wall       = kwa('',       'left_wall')
    period          = kwa(False,    'period')
    context         = kwa(1,        'context')
    window          = kwa('mst',    'window')
    weighting       = kwa('ppmi',   'weighting')
    #? distance     = kwa(??,       'distance')     # FIXME
    group           = kwa(True,     'group')
    word_space      = kwa('vectors', 'word_space')
    dim_max         = kwa(100,      'dim_max')
    sv_min          = kwa(0.1,      'sv_min')
    dim_reduction   = kwa('svm',    'dim_reduction')
    clustering      = kwa('kmeans', 'clustering')
    if isinstance(clustering, list):
        clustering = tuple(clustering)
    cluster_range   = kwa((2,48,1), 'cluster_range')
    if isinstance(cluster_range, list):
        cluster_range = tuple(cluster_range)
    cluster_criteria = kwa('silhouette', 'cluster_criteria')
    cluster_level   = kwa(0.9,      'cluster_level')
    cats_gen        = kwa('off',    'categories_generalization')
    cats_merge      = kwa(0.8,      'categories_merge')
    cats_aggr       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    rules_gen       = kwa('off',    'rules_generalization')
    rules_merge     = kwa(0.8,      'rules_merge')
    rules_aggr      = kwa(0.2,      'rules_aggregation')
    verbose         = kwa('none',   'verbose')
    tmpath          = kwa('',       'tmpath')

    #TODO?: save kwargs ⇒ tmp/file ?


    '''input_parses ⇒ links DataFrame:'''

    files, re01 = check_mst_files(input_parses, verbose)
    log.update(re01)

    #-Save a copy of input parses to prj_dir + '/parses/'  #FIXME:DEL?  #80704
    #-parse_dir = prj_dir + '/parses/'
    #-if check_dir(parse_dir, True, verbose):
    #-    for file in files: copy(file, os.path.dirname(parse_dir))
    #-else: raise FileNotFoundError('File not found', input_parses)

    # group = True    #FIXME: always? False option for context = 0 (words)?

    kwargs['input_files'] = files
    links, re02 = files2links(**kwargs)
    log.update(re02)
    list2file(re02['corpus_stats'], corpus_stats_file)
    #TODO: check write success?
    log.update({'corpus_stats_file': corpus_stats_file})
    if verbose in ['max','debug']:
        print('\n', UTC(),':: learn_grammar:',len(links),'links', type(links))
        with pd.option_context('display.max_rows', 6): print(links, '\n')
        print('\n', UTC(),':: learn_grammar: word_space/clustering:', \
              word_space,'/', clustering, '⇒ category_learner')

    '''Learn word categories'''

    categories, re03 = learn_categories(links, **kwargs)   #80802
    log.update(re03)
    if verbose in ['max','debug']:
        print(UTC(),':: learn_grammar: category_learner returned', \
              len(categories), 'categories', type(categories))

    '''Generalize word categories'''

    #TODO? "gen_cats" ⇒ "categories"? no new name
    if cats_gen == 'jaccard' or (cats_gen == 'auto' and clustering == 'group'):
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar ⇒ generalize_categories (jaccard)')
        gen_cats, re04 = generalize_categories(categories, **kwargs)
        log.update(re04)
    elif cats_gen == 'cosine' or (cats_gen == 'auto' and clustering == 'kmeans'):
        #TODO: vectors g12n
        gen_cats = categories
        log.update({'generalization': 'vector-similarity based - #TODO'})
        if verbose in ['max','debug']:
            print('#TODO: categories generalization based on cosine similarity')
    else:
        gen_cats = categories
        log.update({'generalization': 'error: cats_gen = ' + str(cats_gen)})
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar: generalization = else: cats_gen =', \
                cats_gen, '⇒ gen_cats = categories')

    # Save 1st cats_file = to control 2-step generalization #FIXME:DEL? #80704
    #-re05 = save_cat_tree(gen_cats, output_categories, verbose)
    #-log.update({'category_tree_file': re05['cat_tree_file']})
    #-with open(re05['cat_tree_file'][:-3]+'pkl', 'wb') as f:
    #-    pickle.dump(gen_cats, f)

    '''Learn grammar'''

    if grammar_rules != context:
        context = kwargs['context']
        kwargs['context'] = kwargs['grammar_rules']
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar ⇒ files2links(**kwargs)')
        links, re06 = files2links(**kwargs)
        kwargs['context'] = context

    #TODO: def djs? vectors(disjuncts, **kwargs)

    #if context < 2 and grammar_rules > 1:
    if word_space == 'vectors' or clustering == 'kmeans':
        fat_cats = add_disjuncts(gen_cats, links, verbose)
        #-with open(output_categories + '/fat_cats.pkl', 'wb') as f:
        #-    pickle.dump(fat_cats, f)
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar: back from add_disjuncts')
        #TODO: fat_cats['djs'] = djs(fat_cats[disjuncts], **kwargs)?
    else: fat_cats = gen_cats

    #-rules, re07 = induce_grammar(fat_cats, links)  #80825 added:
    #_"fully connected rules": every cluster connected to all clusters
    if kwargs['grammar_rules'] < 0:
        rules = deepcopy(categories)
        clusters = [i for i,x in enumerate(rules['cluster']) if i>0 and x is not None]
        rule_list = [tuple([-x]) for x in clusters] + [tuple([x]) for x in clusters]
        for cluster in clusters:
            rules['disjuncts'][cluster] = set(rule_list)
    else: rules, re07 = induce_grammar(fat_cats, links)

    if verbose == 'debug':
        print('induce_grammar ⇒ rules:')
        display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
            + [x for i,x in enumerate(cats2list(rules))]))

    lengths = [len(x) for x in rules['disjuncts']]
    if verbose in ['max' ,'debug']:
        print('N clusters = len(rules[disjuncts]-1):',len(rules['disjuncts'])-1)
        print('Rule set lengths:', lengths)
    if verbose == 'debug':
        print('\nrules[disjuncts]:\n', rules['disjuncts'])

    '''Generalize grammar rules'''

    gen_rules = rules
    if 'rules_generalization' in kwargs:
        if kwargs['rules_generalization'] not in ['','off']:
            gen_rules, re08 = generalize_rules(rules, **kwargs)
            log.update(re08)
            if verbose == 'debug':
                print('generalize_rules ⇒ gen_rules:')
                display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
                    + [x for i,x in enumerate(cats2list(gen_rules))]))

    '''Save word category tree, Link Grammar files: cat_tree.txt, dict...dict'''

    re09 = save_cat_tree(gen_rules, output_categories, verbose='none')  #FIXME: verbose?
    #TODO: check file save error?
    log.update(re09)
    re10 = save_link_grammar(gen_rules, output_grammar, grammar_rules)
    log.update(re10)
    log.update({'finish': str(UTC())})

    #TODO: elapsed execution time?  Save log?

    return log


#Notes:

#80802: poc05.py/category_learner ⇒ category_learner.py/learn_categories
#80825: random clusters, interconnected ⇒ cleanup, commit 80828
#TODO: update parameters, update notebooks, remove old notebooks, add warning
