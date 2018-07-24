#!/usr/bin/env python3
#language-learning/src/grammar_learner/poc05.py OpenCog ULL GL POC.0.5 80528-80718
from IPython.display import display
from src.utl.widgets import html_table

# Category Learner  #80625

def group_links(links, verbose):  #80428
    import pandas as pd
    df = links.copy()
    df['links'] = [[x] for x in df['link']]
    del df['link']
    if verbose in ['max','debug']:
        print('\ngroup_links: links:\n')
        with pd.option_context('display.max_rows', 6):
            print(links.sort_values(by='word', ascending=True))
        print('\ngroup_links: df:\n')
        with pd.option_context('display.max_rows', 6): print(df)
    df = df.groupby('word').agg({'links': 'sum', 'count': 'sum'}).reset_index()
    df['words'] = [[x] for x in df['word']]
    del df['word']
    df2 = df.copy().reset_index()
    df2['links'] = df2['links'].apply(lambda x: tuple(sorted(x)))
    df3 = df2.groupby('links')['count'].apply(sum).reset_index()
    if verbose == 'debug':
        with pd.option_context('display.max_rows', 6): print('\ndf3:\n', df3)
    df4 = df2.groupby('links')['words'].apply(sum).reset_index()
    if df4['links'].tolist() == df3['links'].tolist():
        df4['counts'] = df3['count']
    else: print('group_links: line 30 if df4... == df3... ERROR!')
    df4['words'] = df4['words'].apply(lambda x: sorted(list(x)))
    df4['links'] = df4['links'].apply(lambda x: sorted(list(x)))
    df4 = df4[['words','links','counts']].sort_values(by='words', ascending=True)
    df4.index = range(1, len(df4)+1)
    def cluster_id(row): return 'C' + str(row.name).zfill(2)
    df4['cluster'] = df4.apply(cluster_id, axis=1)
    df4 = df4.rename(columns={'words': 'cluster_words', 'links': 'disjuncts'})
    df4 = df4[['cluster', 'cluster_words', 'disjuncts', 'counts']]
    return df4


def category_learner(links, **kwargs):      #80619 POC.0.5
    # links - DataFrame ['word', 'link', 'count']
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    #-links = kwargs['links']   # links - check?
    cats_file       = kwa('/output','output_categories')   # to define tmpath
    #-dict_path       = kwa('/output', 'output_grammar')   # not used here
    tmpath          = kwa('',       'tmpath')
    parse_mode      = kwa('given',  'parse_mode')
    left_wall       = kwa('',       'left_wall')
    period          = kwa(False,    'period')
    context         = kwa(1,        'context')
    window          = kwa('mst',    'window')
    weighting       = kwa('ppmi',   'weighting')
    #? distance       = kwa(??,   'distance')
    group           = kwa(True,     'group')
    word_space      = kwa('vectors','word_space')
    dim_max         = kwa(100,      'dim_max')
    sv_min          = kwa(0.1,      'sv_min')
    dim_reduction   = kwa('svm',    'dim_reduction')
    clustering      = kwa('kmeans', 'clustering')
    cluster_range   = kwa((2,48,1), 'cluster_range')
    cluster_criteria = kwa('silhouette', 'cluster_criteria')
    cluster_level   = kwa(0.9,      'cluster_level')
    generalization  = kwa('off',    'categories_generalization')
    merge           = kwa(0.8,      'categories_merge')
    aggregate       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    verbose         = kwa('none',   'verbose')

    from src.utl.utl import UTC, round1, round2  #, round3, round4, round5
    from src.space.hyperwords import vector_space_dim, pmisvd
    from src.clustering.kmeans import cluster_words_kmeans
    from src.clustering.poc05 import number_of_clusters, clusters2list
    from src.utl.widgets import html_table, plot2d
    from src.utl.read_files import check_dir #, check_mst_files
    from src.utl.write_files import list2file, save_link_grammar
    #-from src.grammar_learner.poc05 import group_links, \
    #-    aggregate_cosine, aggregate_jaccard, aggregate_word_categories

    from collections import OrderedDict
    log = OrderedDict()
    log.update({'category_learner': '80619'})

    if tmpath == '' or tmpath == 'auto':  # temporary files path
        if '.' not in cats_file: tmpath = cats_file
        else: tmpath = cats_file[:cats_file.rindex('/')]
        if tmpath[-1] != '/': tmpath += '/'
        tmpath += 'tmp/'
        print('tmpath:', tmpath)
    if check_dir(tmpath, True, verbose):
        log.update({'tmpath': tmpath})
    #TODO:ERROR

    if verbose in ['max','debug']:
        print(UTC(),':: category_learner: word_space/clustering:', word_space, '/', clustering)

    #-if word_space == 'vectors':    #80619 Category-Tree-2018-06-19.ipynb
    if context == 1 or word_space[0] in ['v','e'] or clustering == 'kmeans':
        #word_space options: v,e: 'vectors'='embeddings', d,w: 'discrete'='word_vectors'
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner: DRK: context =', \
                str(context)+', word_space: '+word_space+', clustering:', clustering)
        #-dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        #-80420 dict_path ⇒ tmpath :: dir to save vectors.txt
        dim = vector_space_dim(links, tmpath, tmpath, dim_max, sv_min, verbose)
        log.update({'vector_space_dim': dim})
        if verbose in ['mid','max','debug']:
            print(UTC(),':: category_learner: vector space dimensionality:', dim, '⇒ pmisvd')
        #-vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        vdf, sv, re01 = pmisvd(links, tmpath, tmpath, dim)
        log.update(re01)
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner: pmisvd returned vdf, svd, re01')
    #-if clustering == 'kmeans':
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner: ⇒ number_of_clusters')
        n_clusters = number_of_clusters(vdf, cluster_range, clustering,  \
            criteria=cluster_criteria, level=cluster_level, verbose=verbose)
        log.update({'n_clusters': n_clusters})
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner: ⇒ cluster_words_kmeans:', n_clusters, 'clusters')
        clusters, silhouette, inertia = cluster_words_kmeans(vdf, n_clusters)
        log.update({'silhouette': silhouette, 'inertia': inertia})
    #-elif clustering[:5] in ['group','ident']:
    else:
        if verbose in ['max', 'debug']:
            print(UTC(),':: category_learner ⇒ iLE group_links: context =', \
                str(context)+', word_space: '+str(word_space)+', clustering:', clustering)
        #TODO: from src.clustering.grouping import group_links
        clusters = group_links(links, verbose)
        log.update({'n_clusters': len(clusters)})
        if verbose not in ['min','none']:
            print('Total', len(clusters), \
                'clusters of identical lexical entries', type(clusters))

    # Convert clusters DataFrame ⇒ cats {}   #80619 0.5
    #TODO?: if clusters == pd.dataframe:
    if verbose in ['max','debug']:
        print(UTC(),':: category_learner: convert clusters ⇒ cats {}')
    cats = {}  #80609 dict instead of DataFrame
    cats['cluster'] = ['C0'] + clusters['cluster'].tolist()
    cats['parent'] = [0 for x in cats['cluster']]
    cats['words'] = [[]] + [set(x) for x in clusters['cluster_words'].tolist()]
    if 'disjuncts' in clusters:
        cats['disjuncts'] = [[]] + clusters['disjuncts'].tolist()
        djset = set()
        [[djset.add(y) for y in x] for x in cats['disjuncts']]
        djlist = sorted(djset)
        cats['djs'] = [set([djlist.index(x) for x in y if x in djlist]) \
                       for y in cats['disjuncts']]
    if 'counts' in clusters:
        cats['counts'] = [0] + clusters['counts'].tolist()
    if word_space == 'vectors' or clustering == 'kmeans':
        cats['quality'] = [0 for x in cats['words']]
        cats['similarities'] = [[0 for y in x] for x in cats['words']]
    else:
        cats['quality'] = [1 for x in cats['words']]
        cats['quality'][0] = 0
        cats['similarities'] = [[1 for y in x] for x in cats['words']]
        cats['similarities'][0] = [0]
    cats['children'] = [0 for x in cats['words']]

    return cats, log


'''Grammar Learner 0.5 80625'''

def induce_grammar(categories, links, verbose='none'):  #80620 learn_grammar replacement
    # categories: {'cluster': [], 'words': [], ...}
    # links: pd.DataFrame (legacy)
    from src.grammar_learner.generalization import cats2list
    import copy
    if verbose in ['max','debug']:
        print(UTC(),':: induce_grammar: categories.keys():', categories.keys())
    rules = copy.deepcopy(categories)

    clusters = [i for i,x in enumerate(rules['cluster']) if i>0 and x is not None]
    word_clusters = dict()
    for i in clusters:
        for word in rules['words'][i]:
            word_clusters[word] = i

    if verbose in ['max','debug']:
        print('induce_grammar: rules.keys():', rules.keys())
        print('induce_grammar: clusters:', clusters)
        print('induce_grammar: word_clusters:', word_clusters)
        print('induce_grammar: rules ~ categories:')
        from IPython.display import display
        from src.utl.widgets import html_table
        display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
            + [x for i,x in enumerate(cats2list(rules)) if i < 4]))

    for cluster in clusters:
        djs = []
        for rule in categories['disjuncts'][cluster]:  #FIXME: categories ⇒ rules 80621
            # 'a- & was-' ⇒ (-9,-26)
            #+TODO? (-x,-y,z) ⇒ (-x,z), (-y,z) ?
            if type(rule) is str:
                x = rule.split()
                dj = []
                for y in x:
                    if y not in ['&', ' ', '']:
                        if y[-1] == '+':
                            dj.append(word_clusters[y[:-1]])
                        elif y[-1] == '-':
                            dj.append(-1 * word_clusters[y[:-1]])
                        else:
                            print('no sign?', dj)  #TODO:ERROR?
                djs.append(tuple(dj))
                if verbose == 'debug':
                    print('induce_gramma: cluster', cluster, '::', rule, '⇒', tuple(dj))
            #TODO? +elif type(rule) is tuple? connectors - tuples?
        rules['disjuncts'][cluster] = set(djs)
        if verbose == 'debug':
            print('induce_grammar: rules["disjuncts"]['+str(cluster)+']', rules['disjuncts'][cluster])
    #rules['djs'] = copy.deepcopy(rules['disjuncts'])  #TODO: check jaccard with tuples else replace with numbers

    if verbose == 'debug':
        print('induce_grammar: updated disjuncts:')
        from IPython.display import display
        from src.utl.widgets import html_table
        display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
            + [x for i,x in enumerate(cats2list(rules)) if i < 32]))

    return rules, {'learned_rules': \
                    len([x for i,x in enumerate(rules['parent']) if x==0 and i>0]), \
                   'total_clusters': len(rules['cluster']) - 1}


'''Learn Grammar :: Integration'''
'''
def print_kwargs(**kwargs):
    from src.utl.utl import UTC
    print('poc05 learn_grammar kwargs:')
    for k,v in kwargs.items(): print(('- '+k+':                ')[:20], v)
    kwargs['printed'] = str(UTC())
    return kwargs
'''
def learn_grammar(input_parses, output_categories, output_grammar, **kwargs):
    # input_parses - dir with .txt files
    # output_categories - path/file.ext / dir ⇒ auto file name
    # output_grammar    - path/file.ext / dir ⇒ auto file name
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    tmpath          = kwa('',       'tmpath')
    parse_mode      = kwa('lower',  'parse_mode')  # files2links
    left_wall       = kwa('',       'left_wall')
    period          = kwa(False,    'period')
    context         = kwa(1,        'context')
    window          = kwa('mst',    'window')
    weighting       = kwa('ppmi',   'weighting')
    #? distance       = kwa(??,   'distance')
    group           = kwa(True,     'group')
    word_space      = kwa('vectors', 'word_space')
    dim_max         = kwa(100,      'dim_max')
    sv_min          = kwa(0.1,      'sv_min')
    dim_reduction   = kwa('svm',    'dim_reduction')
    clustering      = kwa('kmeans', 'clustering')
    #-cluster_range   = kwa((2,48,1), 'cluster_range')
    #-cluster_criteria = kwa('silhouette', 'cluster_criteria')
    #-cluster_level   = kwa(0.9,      'cluster_level')
    cats_gen        = kwa('off',    'categories_generalization')
    #-cats_merge      = kwa(0.8,      'categories_merge')
    #-cats_aggr       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    rules_gen       = kwa('off',    'rules_generalization')   # 'off', 'cosine', 'jaccard'
    #-rules_merge     = kwa(0.8,      'rules_merge'),   # merge rules with similarity > this 'merge' criteria
    #-rules_aggr      = kwa(0.3,      'rules_aggregation'),   # aggregate rules with similarity > this criteria
    verbose         = kwa('none', 'verbose')

    kwargs['input_parses'] = input_parses
    kwargs['output_categories'] = output_categories
    kwargs['output_grammar'] = output_grammar
    #TODO: if parameter != file: auto file name
    input_dir = input_parses
    #cat_path = output_categories
    #-dict_path = output_grammar

    import os, pickle   #, collections
    from collections import OrderedDict
    import pandas as pd
    from shutil import copy2 as copy
    from src.utl.utl import UTC
    from src.utl.read_files import check_dir, check_mst_files
    from src.space.poc05 import files2links
    from src.clustering.poc05 import clusters2dict
    #+from src.link_grammar.poc05 import category_learner
    #+from src.link_grammar.poc05 import induce_grammar
    from src.utl.write_files import list2file, save_link_grammar, save_cat_tree
    from src.utl.widgets import html_table, plot2d
    from src.grammar_learner.generalization import generalize_categories, \
        reorder, cats2list, generalize_rules #, aggregate, aggregate_word_categories\

    log = OrderedDict({'start': str(UTC()), 'learn_grammar': '80605'})

    #TODO: save kwargs?

    files, re01 = check_mst_files(input_parses, verbose)
    log.update(re01)
    if os.path.isdir(output_categories):
        prj_dir = output_categories
    else:  prj_dir = os.path.dirname(output_categories)
    log.update({'project_directory': prj_dir})
    #-Save a copy of input parses to prj_dir + '/parses/'  #FIXME:DEL?    #80704
    #-parse_dir = prj_dir + '/parses/'
    #-if check_dir(parse_dir, True, verbose):
    #-    for file in files: copy(file, os.path.dirname(parse_dir))
    #-else: raise FileNotFoundError('File not found', input_parses)

    # group = True    #? always? False option for context = 0 (words)?
    kwargs['input_files'] = files

    # files ⇒ links:
    links, re02 = files2links(**kwargs)
    log.update(re02)
    list2file(re02['corpus_stats'], prj_dir+'/corpus_stats.txt')
    log.update({'corpus_stats_file': prj_dir+'/corpus_stats.txt'})
    if verbose in ['max','debug']:
        print('\n', UTC(),':: files2links returns links', type(links), ':\n')
        with pd.option_context('display.max_rows', 6): print(links, '\n')
        print('learn_grammar: word_space/clustering:', \
              word_space,'/', clustering, '⇒ category_learner')

    # Learn categories #80619
    categories, re03 = category_learner(links, **kwargs)   #v.0.5 categories: {}
    log.update(re03)
    if verbose in ['max','debug']:
        print(UTC(),':: learn_grammar: category_learner returned', \
              type(categories), 'categories')

    # Generalize categories   #TODO? "gen_cats" ⇒ "categories"? no new name
    if cats_gen == 'jaccard' or (cats_gen == 'auto' and clustering == 'group'):
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar ⇒ generalize_categories (jaccard)')
        gen_cats, re04 = generalize_categories(categories, **kwargs)
        log.update(re04)
    elif cats_gen == 'cosine' or (cats_gen == 'auto' and clustering == 'kmeans'):
        #TODO: vectors g12n
        gen_cats = categories
        log.update({'generalization': 'vector-similarity based - #TODO'})
        if verbose == 'debug':
            print('#TODO: categories generalization based on cosine similarity')
    else:
        gen_cats = categories
        log.update({'generalization': 'error: cats_gen = ' + str(cats_gen)})
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar: generalization = else: cats_gen =', \
                cats_gen, '⇒ gen_cats = categories')

    # Save 1st cats_file = to control 2-step generalization #FIXME:DEL?   #80704
    #-re05 = save_cat_tree(gen_cats, output_categories, verbose)
    #-log.update({'category_tree_file': re05['cat_tree_file']})
    # Save cats.pkl
    #-with open(re05['cat_tree_file'][:-3]+'pkl', 'wb') as f: #FIXME:DEL? #80704
    #-    pickle.dump(gen_cats, f)
    #-if verbose in ['max','debug']:
    #-    print(UTC(),':: learn_grammar: 1st cat_tree saved')

    # Learn grammar

    if grammar_rules != context:
        context = kwargs['context']
        kwargs['context'] = kwargs['grammar_rules']
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar ⇒ files2links(**kwargs)')
        links, re06 = files2links(**kwargs)
        kwargs['context'] = context

    # add disjuncts to categories {} after k-means clustering
    def add_disjuncts(cats, links, verbose='none'):
        # cats: {}
        from copy import deepcopy
        fat_cats = deepcopy(cats)
        top_clusters = [i for i,x in enumerate(cats['cluster']) \
                        if i > 0 and x is not None]
        #word_clusters = {x:i for i,x in enumerate(top_clusters)}
        word_clusters = dict()   #TODO: comprehension?
        for i in top_clusters:
            for word in cats['words'][i]:
                word_clusters[word] = i

        df = links.copy()
        df['cluster'] = df['word'].apply(lambda x: word_clusters[x])
        cdf = df.groupby('cluster').sum().reset_index()
        fat_cats['counts'] = [0] + cdf['count'].tolist()

        fat_cats['disjuncts'] = [[]]
        cdf = df.groupby(['cluster','link'], as_index=False).sum() \
            .sort_values(by=['cluster','count'], ascending=[True,False])
        for cluster in top_clusters:
            ccdf = cdf.loc[cdf['cluster'] == cluster]
            fat_cats['disjuncts'].append(ccdf['link'].tolist())

        fat_cats['djs'] = [[]]
        ldf = df[['link','count']].copy().groupby('link').sum() \
            .sort_values(by='count', ascending=False).reset_index()
        djdict = {x:i for i,x in enumerate(ldf['link'].tolist())}
        df.drop(['word'], axis=1, inplace=True)
        df['dj'] = df['link'].apply(lambda x: djdict[x])
        cdf = df.groupby(['cluster','dj'], as_index=False).sum() \
                .sort_values(by=['cluster','dj'], ascending=[True,True])
        for cluster in top_clusters:
            ccdf = cdf.loc[cdf['cluster'] == cluster]
            fat_cats['djs'].append(ccdf['dj'].tolist())
        return fat_cats

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

    # Learn Grammar
    #+from src.grammar_learner.poc05 import induce_grammar
    rules, re07 = induce_grammar(fat_cats, links)
    if verbose == 'debug':
        print('induce_grammar ⇒ rules:')
        display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
            + [x for i,x in enumerate(cats2list(rules))]))

    # Generalize grammar rules
    gen_rules = rules
    if 'rules_generalization' in kwargs:
        if kwargs['rules_generalization'] not in ['','off']:
            #-word_clusters, re06 = generalize_rules(rule_list, **kwargs)
            from src.grammar_learner.generalization import generalize_rules
            gen_rules, re08 = generalize_rules(rules, **kwargs)
            log.update(re08)
            if verbose == 'debug':
                print('generalize_rules ⇒ gen_rules:')
                display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
                    + [x for i,x in enumerate(cats2list(gen_rules))]))

    # Save cat_tree.txt file
    #^from src.utl.write_files import save_cat_tree
    re09 = save_cat_tree(gen_rules, output_categories, verbose='none')  #FIXME: verbose?
    #TODO: check file save error?
    log.update(re09)
    # Save Link Grammar .dict
    re10 = save_link_grammar(gen_rules, output_grammar, grammar_rules)
    log.update(re10)
    log.update({'finish': str(UTC())})

    #TODO: elapsed execution time?  Save log?
    return log


'''Metrics'''

def params(corpus, dataset, module_path, out_dir, **kwargs):
    from src.utl.read_files import check_dir
    input_parses = module_path + '/data/' + corpus + '/' + dataset
    if check_dir(input_parses, create=False, verbose='min'):
        batch_dir = out_dir + '/' + corpus
        spaces = ['connectors', 'disjuncts']
        if kwargs['word_space'] == 'vectors': wtf = 'DRK'
        else: wtf = 'ILE'
        if kwargs['left_wall'] in ['','none']:
            left_wall = 'no-LEFT-WALL'
        else: left_wall = 'LEFT-WALL'
        if kwargs['period']:
            period = 'period'
        else: period = 'no-period'
        generalization = ['no-generalization', 'generalized-categories', \
                          'generalized-rules', 'generalized-categories-and-rules']
        gen = 0
        if 'categories_generalization' in kwargs:
            if kwargs['categories_generalization'] not in ['','off','none']: gen += 1
        if 'rules_generalization' in kwargs:
            if kwargs['rules_generalization'] not in ['','off','none']:  gen += 2
        prj_dir = batch_dir + '_' + dataset  + '_' + \
            spaces[kwargs['context']-1] + '-'+wtf+'-' + spaces[kwargs['grammar_rules']-1] \
            + '_' + left_wall + '_' + period + '_' + generalization[gen]

        #-print('params - kwargs[rules_generalization]:', kwargs['rules_generalization'])
        #-print('params - kwargs[categories_generalization]:', kwargs['categories_generalization'])
        #-print('params - generalization['+str(gen)+'] =', generalization[gen])
        #-print('params - prj_dir:', prj_dir)

        if check_dir(prj_dir, create=True, verbose='none'):
            output_categories = prj_dir     # no file name ⇒ auto file name
            output_grammar = prj_dir        # no file name ⇒ auto file name
            return input_parses, output_categories, output_grammar
        else: return input_parses, out_dir, out_dir
    else: raise FileNotFoundError('File not found', input_parses)

'''
from src.link_grammar.lgparse import *
from src.link_grammar.cliutils import *
from src.link_grammar.optconst import *

def parse_metrics(dict_path, **kwargs): #80515
    if('test_corpus') in kwargs:
        test_corpus = kwargs['test_corpus']
    if('reference_path') in kwargs:
        ref_path = kwargs['reference_path']
    #TODO*3: else raise error
    if('template_path') in kwargs:
        template_path = kwargs['template_path']
    else: template_path = 'en'
    if('linkage_limit') in kwargs:
        linkage_limit = kwargs['linkage_limit']
    else: linkage_limit = 1

    import os, sys
    from shutil import copy2 as copy
    #^from link_grammar.lgparse import *
    #^from link_grammar.cliutils import *
    #^from link_grammar.optconst import *
    #^SyntaxError: import * only allowed at module level
    if os.path.isfile(dict_path):
        output_path = os.path.dirname(dict_path)   # Output directory path to store parse text files in.
    elif os.path.isdir(dict_path):
        output_path = dict_path
    #else: print('.dict file error:', dict_file)
    grammar_path = output_path

    # Generate LG diagram output
    input_path = test_corpus
    options = 0x00000000 | BIT_ULL_IN | BIT_STRIP | BIT_LG_EXE | BIT_NO_LWALL | BIT_RM_DIR | BIT_OUTPUT_DIAGRAM #  | BIT_DPATH_CREATE
    parse_corpus_files(input_path, output_path, dict_path, grammar_path, template_path,
                       linkage_limit, options);
    for root, dirs, files in os.walk(output_path):
        for file in files:
            if file.endswith(".diag2") and root != output_path:
                new_diag2 = os.path.join(root, file)
                old_diag2 = os.path.join(output_path, file)
                if os.path.isfile(old_diag2): os.remove(old_diag2)
                copy(new_diag2, output_path)

    # Generate ULL output & parseability estimation
    options = 0x00000000 | BIT_ULL_IN | BIT_STRIP | BIT_LG_EXE | BIT_NO_LWALL | BIT_RM_DIR # | BIT_DPATH_CREATE
    parse_corpus_files(input_path, output_path, dict_path, grammar_path, template_path,
                       linkage_limit, options);
    for root, dirs, files in os.walk(output_path):
        for file in files:
            if file.endswith(".stat2"):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.read().splitlines()
            elif file.endswith(".ull2"):
                ull_path = os.path.join(root, file)
    parse_ability = int(round(float(lines[-2].split('\t')[-1][:-1]),0));

    # Parse Quality:
    from src.link_grammar.evaluate_80515 import compare_ull_files
    # evaluate_80515.py - hacked version vy @alex
    compare_ull_files(ull_path, ref_path, False, True)
    for root, dirs, files in os.walk(output_path):
        for file in files:
            if file.endswith(".qc"):
                with open(os.path.join(root, file), 'r') as f:
                    lines = f.read().splitlines()
    parse_quality = int(round(float(lines[2].split()[-1][:-1]),0))

    return parse_ability, parse_quality, old_diag2


def run_learn_grammar(corpus, dataset, module_path, out_dir, **kwargs): #80411
    from src.grammar_learner.poc05 import parse_metrics
    input_parses, output_categories, output_grammar = \
        params(corpus, dataset, module_path, out_dir, **kwargs)
    #TODO: check out_dir - absolute/relative ⇒ add module_path
    response = learn_grammar(input_parses, output_categories, output_grammar, **kwargs)
    dict_path = response['grammar_file']
    pa, pq, lg_parse_path = parse_metrics(dict_path, **kwargs)
    response['parse_ability'] = pa
    response['parse_quality'] = pq
    response['parse_quability'] = int(round(pa*pq/100,0))
    response['lg_parse_file'] = lg_parse_path
    return response
'''
#_Notes

#80419 update links2stalks strict_rules ⇒ changes in disjunct-based rules !:)
#80511 0.4 kwargs, params, run_learn_grammar
#80523 0.4 save category tree
#80629 0.5 hierarchical cat_tree ⇒ agglomerative generalization
#80718 update git push from 94..server
