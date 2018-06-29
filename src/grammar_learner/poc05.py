#!/usr/bin/env python3
#/src/grammar_learner/poc05.py OpenCog ULL Grammar Learner POC.0.5 80528-80629
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

#-def aggregate_cosine(clusters, generalization = 'cosine',
#-    merge = 0.8, aggregate = 0.2, grammar_rules = 1, verbose = 'none'):
def aggregate_cosine(clusters, **kwargs):   #80523
    # clusters - pd.DataFrame(['cluster', 'cluster_words', 'disjuncts'])
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    aggregation     = kwa('off',    'categories_generalization')
    merge           = kwa(0.8,      'categories_merge')
    aggregate       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    verbose         = kwa('none',   'verbose')
    if verbose in ['debug', 'max']:
        print('Cosine similarity based aggregation')
    import numpy as np
    from src.clustering.similarity import cluster_similarity
    from src.utl.utl import round1, round2 #, round3, round4, round5

    categories = clusters.copy()
    sim_df, response = cluster_similarity(clusters, 'max')
    if verbose in ['max','debug']:
        count, division = np.histogram(sim_df['similarity'])
        sim_df['similarity'].hist(bins=division)
        print('Cluster similarities: absolute values >', aggregate, ':')
        print(sim_df[['c1','c2', 'similarity']].loc[abs(sim_df['similarity']) > merge])
        #print(clusters.applymap(round1))
    for index, row in sim_df.loc[abs(sim_df['similarity']) > aggregate].iterrows():
        print('row:', row)
    return categories, response

def aggregate_jaccard(clusters, step='categories', **kwargs):
    # clusters - pd.DataFrame(['cluster', 'cluster_words', 'disjuncts'])
    # step = 'categories' / 'rules' = GL stage of generalization
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    grammar_rules   = kwa(1, 'grammar_rules')
    if step[0] == 'r':  # 'rules'
        aggregation = kwa('off','rules_generalization')
        merge       = kwa(0.8,  'rules_merge')
        aggregate   = kwa(0.2,  'rules_aggregation')
    else:
        aggregation = kwa('off','categories_generalization')
        merge       = kwa(0.8,  'categories_merge')
        aggregate   = kwa(0.2,  'categories_aggregation')
    verbose         = kwa('none', 'verbose')
    if verbose in ['debug', 'max']:
        print('Jaccard index based aggregation')

    categories = clusters.copy()
    disjuncts = clusters['disjuncts'].tolist()
    djset = set()
    [[djset.add(y) for y in x] for x in disjuncts]
    djlist = sorted(djset)
    djs = [set([djlist.index(x) for x in y if x in djlist]) for y in disjuncts]
    similarities = []       #similarity matrix FIXME:DEL?
    similar_disjuncts = []
    similarity_thresholds = {}

    def jaccard(x,y): return len(x.intersection(y))/len(x.union(y))

    for i,x in enumerate(djs):
        lst = []
        similar_disjuncts.append([])
        for j,y in enumerate(djs):
            similarity = jaccard(x,y)
            if similarity > aggregate:
                similar_disjuncts[i].append(j)
            round_sim = round(similarity,2)
            lst.append(round_sim)
            if round_sim > 0.0 and round_sim < 1.0:
                if round_sim in similarity_thresholds:
                    similarity_thresholds[round_sim] += 1
                else: similarity_thresholds[round_sim] = 1
        similarities.append(lst)
    if verbose in ['max', 'debug']:
        print('\nsimilarities:')
        for x in similarities: print(x)
        print('\nsimilar_disjuncts:', similar_disjuncts)
    merges = [x for x in similar_disjuncts if len(x) > 1]
    cats = [i for i,x in enumerate(disjuncts)]
    for x in merges:
        for z in x: cats[z] = min([cats[y] for y in x])
    dct = {}
    for i,x in enumerate(sorted(set(cats))): dct[x] = i+1
    categories['cluster'] = ['C' + str(dct[x]).zfill(2) for x in cats]
    if verbose in ['debug', 'max']:
        print('aggregate_jaccard: similarities:\n', similarities)
        print('\naggregate_jaccard: categories:\n', categories)
    #-return categories, {'similaritiy_matrix': similarities}
    return categories, {'similarity_thresholds': similarity_thresholds}

def aggregate_word_categories(clusters, **kwargs):  #80523
    # clusters - pd.DataFrame(['cluster', 'cluster_words', 'disjuncts'])
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    aggregation     = kwa('off',    'categories_generalization')
    merge           = kwa(0.8,      'categories_merge')
    aggregate       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    verbose         = kwa('none',   'verbose')

    categories = clusters
    log = {'aggregation': aggregation}
    if aggregation == 'auto':
        if 'disjuncts' in clusters:
            categories, response = aggregate_jaccard(clusters, 'cats', **kwargs)
        else: categories, response = aggregate_cosine(clusters, **kwargs)
    elif aggregation == 'cosine':
        categories, response = aggregate_cosine(clusters, **kwargs)
    elif aggregation == 'jaccard':
        categories, response = aggregate_jaccard(clusters, 'categories', **kwargs)
    else:
        categories = clusters
        response = {'error': 'aggregate_word_categories - method choice?'}
    log.update(response)
    cats_number = len(set(categories['cluster'].tolist()))
    log.update({'categories': cats_number})
    return categories, log


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

    if verbose == 'debug':
        print('category_learner: word_space:', word_space, '/ clustering:', clustering)

    #-if word_space == 'vectors':    #80619 Category-Tree-2018-06-19.ipynb
    if context == 1 or word_space[0] in ['v','e'] or clustering == 'kmeans':
        #word_space options: v,e: 'vectors'='embeddings', d,w: 'discrete'='word_vectors'
        print('DRK: context =', str(context)+', word_space: '+word_space+', clustering:', clustering)
        #-dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        #-80420 dict_path ⇒ tmpath :: dir to save vectors.txt
        dim = vector_space_dim(links, tmpath, tmpath, dim_max, sv_min, verbose)
        log.update({'vector_space_dim': dim})
        if verbose in ['mid','max','debug']:
            print('Optimal vector space dimensionality:', dim)
        #-vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        vdf, sv, re01 = pmisvd(links, tmpath, tmpath, dim)
        log.update(re01)
    #-if clustering == 'kmeans':
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner ⇒ number_of_clusters')
        n_clusters = number_of_clusters(vdf, cluster_range, clustering,  \
            criteria=cluster_criteria, level=cluster_level, verbose=verbose)
        log.update({'n_clusters': n_clusters})
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner ⇒ cluster_words_kmeans:', n_clusters, 'clusters')
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


# Grammar Learner 0.4 legacy

def clusters2dict(clusters, verbose='none'):
    #_convert clusters versions ⇒ unified dictionary {word: cluster}
    if isinstance(clusters, dict):  #
        return clusters
    elif isinstance(clusters, list): # category_list
        d = dict()
        for row in clusters:
            for word in row[3]: d[word] = row[1]
        return d
    if isinstance(clusters, pd.DataFrame):
        if 'germs' in clusters:
            d = dict()
            for row in clusters.itertuples():
                for word in row[1]: d[word] = row[4]
            if verbose == 'max': print('germs!')
            return d
        else:
            d = dict()
            for row in clusters.itertuples():
                for word in row[2]: d[word] = row[1]
            if verbose == 'max': print('no germs')
            return d

def links2stalks(links, clusters, grammar_rules = 1, verbose='none'):
    '''
    TODO: debug errors on OOV -- out of clusters dict words
    '''
    # grammar_rules: 'connectors', 'disjuncts'
    if verbose == 'debug': print('\nlinks2stalks\n')
    import pandas as pd
    #^from src.grammar_learner.poc3 import clusters2dict
    if isinstance(clusters, dict): word_clusters = clusters
    else: word_clusters = clusters2dict(clusters, verbose)
    #80428 0.4 ipynb :: feed word_clusters dict -- make standard, DEL checks

    def link2links(link):
        if '&' not in link:
            if link[-1] in ['-','+']:
                return word_clusters[link[:-1]] + link[-1]
            else: return link
        else:
            return ' & '.join([word_clusters[x[:-1]] + x[-1] \
                for x in link.split() if x != '&' and x[:-1] in word_clusters])
                #for x in link.split()if x != '&']) #FIXED 80507

    def relaxed_rules(x):   # (c) Anton: ({a- or b-} & {c+ or d+}) or ({a-} & {c+})
        #TODO: split disjuncts? OR just ignore?
        z = [y for y in x[1:] if '&' not in y]   #80405 ignore disjuncts - gut??
        lefts = sorted(set([y for y in z if y[-1] == '-']))
        rights = sorted(set([y for y in z if y[-1] == '+']))
        disjuncts = []
        if len(lefts) > 0 and len(rights) > 0:
            left = '{' + ' or '.join([y[:-1]+x[0]+'-' for y in lefts]) + '}'
            right = '{' + ' or '.join([x[0]+y for y in rights]) + '}'
            disjuncts.append(left + ' & ' + right)
        elif len(lefts) > 0 and len(rights) == 0:
            disjuncts.append(' or '.join([y[:-1]+x[0]+'-' for y in lefts]))
        elif len(lefts) == 0 and len(rights) > 0:
            disjuncts.append(' or '.join([x[0]+y for y in rights]))
        return disjuncts

    def strict_rules(x):    # 80419
        if verbose == 'debug': print('links2stalks ⇒ strict_rules')
        disjuncts = []
        for y in x[1:]:
            if '&' in y:
                def f(z):  #! inside only: not pure - uses scope x[0] :(
                    if z[-1] == '-':
                        return z[:-1] + x[0] + '-'
                    else: return x[0] + z
                disjuncts.append(' & '.join([f(z) for z in y.split() if z != '&']))
            elif y[-1] == '-':
                disjuncts.append(y[:-1]+x[0]+'-')
            elif y[-1] == '+':
                disjuncts.append(x[0]+y)
        disjuncts = sorted(set(disjuncts))
        #-disjuncts.sort()
        return disjuncts

    if verbose == 'debug': print('\nlinks:\n', links)
    df = links.copy()
    df['links'] = df['link'].apply(link2links)
    df['links'] = [[x] for x in df['links']]
    stalks = df.groupby('word').agg({'links': 'sum', 'count': 'sum'}).reset_index()
    #-stalks['links'] = stalks['links'].apply(dedupe)
    stalks['links'] = stalks['links'].apply(lambda x: sorted(set(x)))
    stalks['cluster'] = stalks['word'].apply(lambda x: word_clusters[x])
    stalks['[clstr]'] = [[x] for x in stalks['cluster']]
    stalks['cluster_links'] = stalks['[clstr]'] + stalks['links']
    del stalks['[clstr]']
    del stalks['links']
    if verbose == 'debug':
        print('\nstalks:', type(stalks))
        with pd.option_context('display.max_rows', 6): print(stalks, '\n')

    if grammar_rules == 1:
        if verbose == 'debug': print('links2stalks: connectors ⇒ «relaxed_rules»')
        #-stalks['disjuncts'] = [[x] for x in stalks['disjuncts']]
        stalks['disjuncts'] = stalks['cluster_links'].apply(relaxed_rules)
        if verbose == 'debug': print('type(stalks["disjuncts"]):', type(stalks['disjuncts']))
    else:
        if verbose == 'debug': print('links2stalks: disjuncts ⇒ strict_rules')
        stalks['disjuncts'] = stalks['cluster_links'].apply(strict_rules)
        if verbose == 'debug': print('type(stalks["disjuncts"]):', type(stalks['disjuncts']))
    del stalks['cluster_links']
    stalks['words'] = [[x] for x in stalks['word']]
    del stalks['word']
    if verbose == 'debug': print('\nstalks:\n', stalks)
    return stalks

def grammar_learner(clusters, links, **kwargs):  #80620 replaced by imduce_grammar
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    grammar_rules   = kwa(1, 'grammar_rules')
    verbose         = kwa('none', 'verbose')

    stalks = links2stalks(links, clusters, grammar_rules, verbose)
    rules = stalks.groupby('cluster') \
        .agg({'words': 'sum', 'disjuncts': 'sum', 'count': 'sum'}).reset_index()

    rules['disjuncts'] = rules['disjuncts'].apply(lambda x: sorted(set(x)))
    #FIXME: remove duplicate disjuncts!

    rule_list = list()
    for row in rules.itertuples():
        rule = []
        rule.append(row[1])     # Cluster
        rule.append(row[2])     # Words
        rule.append([])         # Left Connectors
        rule.append([])         # Right Connectors
        rule.append(row[3])     # Disjuncts
        rule_list.append(rule)
    rule_list.sort()
    return rule_list, {'rule_list': len(rule_list)}


'''Grammar Learner 0.5 80625'''

def induce_grammar(categories, links, verbose='none'):  #80620 learn_grammar replacement
    # categories: {'cluster': [], 'words': [], ...}
    # links: pd.DataFrame (legacy)
    from src.grammar_learner.generalization import cats2list
    import copy
    rules = copy.deepcopy(categories)

    clusters = [i for i,x in enumerate(rules['cluster']) if i>0 and x is not None]
    word_clusters = dict()
    for i in clusters:
        for word in rules['words'][i]:
            word_clusters[word] = i

    if verbose == 'debug':
        print('induce_grammar: rules.keys():', rules.keys())
        print('induce_grammar: clusters:', clusters)
        print('induce_grammar: word_clusters:', word_clusters)
        print('induce_grammar: rules ~ categories:')
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

def print_kwargs(**kwargs):
    from src.utl.utl import UTC
    print('poc04 learn_grammar kwargs:')
    for k,v in kwargs.items(): print(('- '+k+':                ')[:20], v)
    kwargs['printed'] = str(UTC())
    return kwargs

def learn_grammar(input_parses, output_categories, output_grammar, **kwargs):
    # input_parses - dir with .txt files
    # output_categories - path/file.ext / dir ⇒ auto file name
    # output_grammar    - path/file.ext / dir ⇒ auto file name
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    tmpath          = kwa('',       'tmpath')
    parse_mode      = kwa('given',  'parse_mode')
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

    print('learn_grammar: grammar_rules:', grammar_rules)

    #80509 TODO: renamed parameters ⇒ update code
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
    from src.space.poc05 import files2links   #80528 .poc05
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
    parse_dir = prj_dir + '/parses/'
    if check_dir(parse_dir, True, verbose):
        for file in files: copy(file, os.path.dirname(parse_dir))
    else: raise FileNotFoundError('File not found', input_parses)
    # group = True    #? always? False option for context = 0 (words)?
    kwargs['input_files'] = files

    # files ⇒ links:
    links, re02 = files2links(**kwargs)
    log.update(re02)
    # corpus_stats - implanted in files2links 80605
    list2file(re02['corpus_stats'], prj_dir+'/corpus_stats.txt')
    log.update({'corpus_stats_file': prj_dir+'/corpus_stats.txt'})
    if verbose in ['max','debug']:
        print('\nfiles2links returns links', type(links), ':\n')
        with pd.option_context('display.max_rows', 6): print(links, '\n')
        print('learn_grammar: word_space:', word_space, '/ clustering:', clustering)

    # Learn categories: new 80619
    categories, re03 = category_learner(links, **kwargs)   #v.0.5 categories: {}
    log.update(re03)

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
            print(UTC(),':: learn_grammar: generalization: else: cats_gen =', cats_gen, '⇒ gen_cats = categories')

    # Save 1st cats_file = to control 2-step generalization #FIXME:DEL?
    re05 = save_cat_tree(gen_cats, output_categories, verbose)  #FIXME: verbose?
    #TODO: check file save error?
    log.update({'category_tree_file': re05['cat_tree_file']})

    with open(re05['cat_tree_file'][:-3]+'pkl', 'wb') as f: #FIXME:DEL tmp 80601
        pickle.dump(gen_cats, f)
    if verbose in ['max','debug']:
        print(UTC(),':: learn_grammar: 1st cat_tree saved')

    # Learn grammar     #80623

    if grammar_rules != context:
        context = kwargs['context']
        kwargs['context'] = kwargs['grammar_rules']
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar ⇒ files2links(**kwargs)')
        links, re06 = files2links(**kwargs)
        kwargs['context'] = context

    # add disjuncts to categories {}  after k-means clustering  #TOEO: speed!
    def add_disjuncts(cats, links, verbose='none'):
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: cats:', len(cats['cluster']), 'clusters')
        from copy import deepcopy
        top_clusters = [i for i,x in enumerate(cats['cluster']) \
                        if i > 0 and x is not None]
        word_clusters = dict()
        for i in top_clusters:
            for word in cats['words'][i]:
                word_clusters[word] = i
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: word_clusters:', len(word_clusters), 'words')
        df = links.copy()
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: df[links] = [[x] for x in df[link]]')
        df['links'] = [[x] for x in df['link']]
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: df[cluster] = df[word].apply(lambda x: word_clusters[x])')
        df['cluster'] = df['word'].apply(lambda x: word_clusters[x])
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: cdf = df.groupby("cluster").agg(...')
        cdf = df.groupby('cluster').agg({'links': 'sum', 'count': 'sum'}).reset_index()
        #TODO? del df[...] to free RAM?
        disjuncts = [[]] + cdf['links'].tolist()
        counts = [0] + cdf['count'].tolist()
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: len(cluster, disjuncts):', \
                  len(rules['cluster']), len(disjuncts), '\ncounts:', counts)
        fat_cats = deepcopy(cats)
        fat_cats['counts'] = [0] + cdf['count'].tolist()
        fat_cats['disjuncts'] = [[]] + cdf['links'].tolist()
        #['djs']
        djset = set()
        [[djset.add(y) for y in x] for x in fat_cats['disjuncts']]
        djlist = sorted(djset)
        fat_cats['djs'] = [set([djlist.index(x) for x in y if x in djlist]) \
                           for y in fat_cats['disjuncts']]
        if verbose in ['max','debug']:
            print(UTC(),':: add_disjuncts: return fat_cats')
        return fat_cats

    #TODO: def djs? vectors(disjuncts, **kwargs)

    #if context < 2 and grammar_rules > 1:
    if word_space == 'vectors' or clustering == 'kmeans':
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar ⇒ add_disjuncts')
            #with open(re05['cat_tree_file'][:-9]+'s.pkl', 'wb') as f: #FIXME:DEL tmp 80601
            #    pickle.dump(gen_cats, f)

        fat_cats = add_disjuncts(gen_cats, links)
        if verbose in ['max','debug']:
            print(UTC(),':: learn_grammar: back from add_disjuncts')
        #TODO: fat_cats['djs'] = djs(fat_cats[disjuncts], **kwargs)   #TODO:
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
                    + [x for i,x in enumerate(cats2list(rulez))]))

    # Save cat_tree.txt file
    #-from src.utl.write_files import save_cat_tree
    re09 = save_cat_tree(gen_rules, output_categories, verbose='none')  #FIXME: verbose?
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
        generalization = ['no_generalization', 'generalized_categories', \
                          'generalized_rules', 'generalized_categories_and_rules']
        gen = 0
        if 'categories_generalization' in kwargs:
            if kwargs['categories_generalization'] not in ['','off']: gen += 1
        if 'rules_generalization' in kwargs:
            if kwargs['rules_generalization'] not in ['','off']:  gen += 2
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

#_Notes

#80419 update links2stalks strict_rules ⇒ changes in disjunct-based rules !:)
#80511 0.4 kwargs, params, run_learn_grammar
#80523 0.4 save category tree
#80629 0.5 hierarchical cat_tree ⇒ agglomerative generalization
