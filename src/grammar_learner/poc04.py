#!/usr/bin/env python3
#/src/grammar_learner/poc04.py OpenCog ULL Grammar Learner POC 0.4 80426-80525

# Category Learner  #80428

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

def category_learner(links, **kwargs):  #80509+10
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
    from src.clustering.poc04 import number_of_clusters, clusters2list
    from src.utl.widgets import html_table, plot2d
    from src.utl.write_files import list2file
    from src.link_grammar.poc import save_link_grammar

    from collections import OrderedDict
    log = OrderedDict()
    log.update({'category_learner': '80525'})

    if tmpath == '' or tmpath == 'auto':  # temporary files path
        if '.' not in cats_file: tmpath = cats_file
        else: tmpath = cats_file[:cats_file.rindex('/')]
        if tmpath[-1] != '/': tmpath += '/'
        tmpath += 'tmp'

    #-print('poc04.category_learner: tmpath = ', tmpath)

    if verbose == 'debug':
        print('category_learner: word_space:', word_space, '/ clustering:', clustering)

    if word_space == 'vectors':
        #^from src.space.hyperwords import vector_space_dim, pmisvd
        #-dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        #-80420 dict_path ⇒ tmpath :: dir to save vectors.txt
        dim = vector_space_dim(links, tmpath, tmpath, dim_max, sv_min, verbose)
        log.update({'vector_space_dim': dim})
        if verbose == 'min': print('Optimal vector space dimensionality:', dim)
        #-vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        #-80420 dict_path ⇒ tmpath :: dir to save vectors.txt
        vdf, sv, re01 = pmisvd(links, tmpath, tmpath, dim)
        log.update(re01)
    elif verbose in ['max','debug']:
        print('category_learner: word_space:', word_space, '/ clustering:', clustering)

    if clustering == 'kmeans':
        #^from src.clustering.kmeans import cluster_words_kmeans
        #^from src.clustering.poc03 import number_of_clusters, clusters2list
        n_clusters = number_of_clusters(vdf, cluster_range ,clustering,  \
            criteria=cluster_criteria, level=cluster_level, verbose=verbose)
        clusters, silhouette, inertia = cluster_words_kmeans(vdf, n_clusters)
        if verbose not in ['min','none']:
            print('/poc04/category_learner: number of clusters =', n_clusters)
        if verbose in ['max','debug']: print(clusters.applymap(round2))
        if verbose in ['max','debug']:  #80412 hack: plots for AGI-2018 :(
            if context == 1:            #FIXME:DEL?
                plot2d(1, 2, clusters, 'cluster_words', 10)
            else:
              if len(clusters) < 6:
                  plot2d(1, 3, clusters, 'cluster_words', 10)
              else: plot2d(1, 4, clusters, 'cluster_words', 10)

    elif clustering[:5] in ['group','ident']:
        if verbose in ['max', 'debug']: print('clustering:', clustering)
        #TODO: from src.clustering.grouping import group_links
        clusters = group_links(links, verbose)
        if verbose not in ['min','none']:
            print('Total', len(clusters), \
                'clusters of identical lexical entries', type(clusters))
        if verbose in ['max','debug']:
            print('\n', clusters[['cluster_words', 'disjuncts']]) #.head(12))

    # Generalization = word categories aggregation

    if generalization in ['auto', 'jaccard', 'cosine']:
        #-print('generalization:', generalization)
        #-categories, res2 = aggregate_word_categories(clusters, \
        #-    generalization, merge, aggregate, grammar_rules, verbose)
        categories, re02 = aggregate_word_categories(clusters, **kwargs) #80510
        log.update(re02)
        #-print(len(categories), 'categories', type(categories), '\n', categories)
    else:
        categories = clusters
        #-print('generalization:', generalization, '⇒ categories = clusters')

    #-Save categories #TODO: return & save outside?
    #^from src.clustering.poc04 import clusters2list
    #^from src.utl.write_files import list2file
    category_list = clusters2list(categories)
    if verbose not in ['min','none']:
        display(html_table([['Code','Parent','Id','Quality','Words','Relevance']] \
            + category_list))
    '''80522: save file outside
    if '.' not in cats_file:  #80508 auto file name
        if cats_file[-1] != '/': cats_file += '/'
        cats_file += (str(len(set(categories['cluster'].tolist()))) + '_categories.txt')
    categories = list2file(category_list, cats_file)
    log.update({'categories_file': cats_file})
    '''
    if verbose in ['debug']:
        print('\nWord categories:\n', categories)
        #for line in categories.splitlines()[:3]: print(line)
    if verbose not in ['min','none']:
        print('\nCategory list -', len(categories), 'lines, saved to', cats_file)

    return category_list, log


# Grammar Learner

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


#def grammar_learner(clusters, links, grammar_rules = 1, verbose='none'):
def grammar_learner(clusters, links, **kwargs):
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    #-clusters        = kwargs['word_clusters']
    #-links           = kwargs['links']
    grammar_rules   = kwa(1, 'grammar_rules')
    verbose         = kwa('none', 'verbose')

    if verbose == 'debug': print('\ngrammar_learner rules =', grammar_rules)
    from src.grammar_learner.poc04 import links2stalks
    from src.utl.turtle import html_table

    stalks = links2stalks(links, clusters, grammar_rules, verbose)
    rules = stalks.groupby('cluster') \
        .agg({'words': 'sum', 'disjuncts': 'sum', 'count': 'sum'}).reset_index()
    rules['disjuncts'] = rules['disjuncts'].apply(lambda x: sorted(set(x)))
    if verbose == 'debug': print('\nrules', type(rules), '\n', rules)
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
    if verbose not in ['min','none']:
        display(html_table([['Cluster','Germs','L','R','Disjuncts']] + rule_list))

    return rule_list, {'rule_list': len(rule_list)}


def generalise_rules(rule_list, **kwargs):   # 80522 generaliZe replacement
    from src.clustering.poc04 import clusters2list
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    #-clusters        = kwargs['word_clusters']
    #-links           = kwargs['links']
    generalization  = kwa('off', 'rules_generalization')  # 'off', 'cosine', 'jaccard'
    merge           = kwa(0.8, 'rules_merge')  # merge rules with similarity > this 'merge' criteria
    aggregate       = kwa(0.2, 'rules_aggregation')  # aggregate rules with similarity > this criteria
    grammar_rules   = kwa(1, 'grammar_rules')
    verbose         = kwa('none', 'verbose')

    log = {'rules_generalization': 'jaccard'}

    if verbose in ['max', 'debug']:
        print('Jaccard index based grammar rules generalisation')
        print('generalise_rules kwargs ⇒ parameters:', \
            '\n- generalization:', generalization, \
            '\n- merge:', merge, \
            '\n- aggregate:', aggregate, \
            '\n- grammar_rules:', grammar_rules)
        print('generaliser: rule_list:', rule_list)

    import pandas as pd
    df = pd.DataFrame(columns=['cluster','cluster_words','disjuncts'])
    for i,x in enumerate(rule_list):
        connectors = []
        for y in x[4]: connectors.append(y.replace(x[0],''))
        df.loc[i] = [x[0], x[1], connectors]
    df.index = range(1, len(df)+1)
    #kwargs['categories_generalization'] =
    categories, response = aggregate_jaccard(df, 'rules', **kwargs)
    category_list = clusters2list(categories)
    #-print('\ngeneraliser: categories\n', categories)
    #-print('\ngeneraliser: response\n', response)
    log.update({'rule_similarity_thresholds': response['similarity_thresholds']})
    return category_list, log

#-def generalize_rules(rule_list, generalization = 'jaccard',
#-    merge = 0.8, aggregate = 0.2, grammar_rules = 1, verbose = 'none'):
def generalize_rules(rule_list, **kwargs):  #80522 replaced FIXME:DEL?
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    #-clusters        = kwargs['word_clusters']
    #-links           = kwargs['links']
    generalization  = kwa('off', 'rules_generalization')  # 'off', 'cosine', 'jaccard'
    merge           = kwa(0.8, 'rules_merge')  # merge rules with similarity > this 'merge' criteria
    aggregate       = kwa(0.2, 'rules_aggregation')  # aggregate rules with similarity > this criteria
    grammar_rules   = kwa(1, 'grammar_rules')
    verbose         = kwa('none', 'verbose')

    if verbose in ['max', 'debug']:
        print('Jaccard index based grammar rules generalization')
        print('generalize_rules kwargs ⇒ parameters:', \
            '\n- generalization:', generalization, \
            '\n- merge:', merge, \
            '\n- aggregate:', aggregate, \
            '\n- grammar_rules:', grammar_rules)

    conn_set = set()
    connectors = list()
    cluster_words = list()
    #cluster_connectors = dict()
    for i,x in enumerate(rule_list):
        connectors.append([])
        cluster_words.append(x[1])
        #cluster_connectors[x[0]] = []
        for y in x[4]:
            conn_set.add(y.replace(x[0],''))
            connectors[i].append(y.replace(x[0],''))
            #cluster_connectors[x[0]].append(y.replace(x[0],''))

    conn_list = sorted(conn_set)
    if verbose in ['max', 'debug']:
        print('connectors:', connectors, '\nconn_list:', conn_list)

    conns = [set([conn_list.index(x) for x in y if x in conn_list]) for y in connectors]

    similarities = []       #FIXME:DEL?
    similarity_thresholds = {}
    similar_conns = []

    def jaccard(x,y):
        return len(x.intersection(y))/len(x.union(y))

    for i,x in enumerate(conns):
        lst = []
        similar_conns.append([])
        for j,y in enumerate(conns):
            similarity = jaccard(x,y)
            if similarity > aggregate:   #80510L merge ⇒ aggregate
                similar_conns[i].append(j)
            round_sim = round(similarity,2)
            lst.append(round_sim)
            if round_sim > 0.0 and round_sim < 1.0:
                if round_sim in similarity_thresholds:
                    similarity_thresholds[round_sim] += 1
                else: similarity_thresholds[round_sim] = 1
        similarities.append(lst)
    if verbose in ['max', 'debug']:
        print('\nconns:', conns)
        print('\nsimilarities:')
        for x in similarities: print(x)
        print('\nsimilar_conns:', similar_conns)

    merges = [x for x in similar_conns if len(x) > 1]
    if verbose in ['max', 'debug']: print('merges:', merges)
    cats = [i for i,x in enumerate(connectors)]
    if verbose in ['max', 'debug']: print('cats:', cats)
    for x in merges:
        for z in x: cats[z] = min([cats[y] for y in x])
    if verbose in ['max', 'debug']: print('cats:', cats)

    dct = {}
    for i,x in enumerate(sorted(set(cats))): dct[x] = i+1
    if verbose in ['max', 'debug']: print('dct:', dct)
    categories = ['C' + str(dct[x]).zfill(2) for x in cats]
    if verbose in ['max', 'debug']: print('categories:', categories)

    if len(categories) == len(cluster_words):
        word_clusters = dict()
        i = 0
        for x in cluster_words:
            for word in x:
                word_clusters[word] = categories[i]
            i += 1
    if verbose in ['max', 'debug']: print('word_clusters:', word_clusters)

    return word_clusters, {'similarity_thresholds': similarity_thresholds}


'''Learn Grammar = Integration'''

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

    #80509 kwargs tests ~OK
    #-print('poc04 learn_grammar kwargs:')
    #-for k,v in kwargs.items(): print(('- '+k+':                ')[:20], v)
    #-response = print_kwargs(**kwargs)
    #-return response
    #80509 TODO: renamed parameters ⇒ update code
    kwargs['input_parses'] = input_parses
    kwargs['output_categories'] = output_categories
    kwargs['output_grammar'] = output_grammar
    #TODO: if parameter != file: auto file name
    input_dir = input_parses
    #cat_path = output_categories
    #-dict_path = output_grammar

    import os   #, collections
    import pandas as pd
    from shutil import copy2 as copy
    from src.utl.utl import UTC
    from src.utl.read_files import check_dir, check_mst_files
    from src.space.poc04 import files2links
    #+from src.link_grammar.poc04 import category_learner
    from src.clustering.poc04 import clusters2dict
    #+from src.link_grammar.poc04 import grammar_learner
    #-from src.link_grammar.poc import save_link_grammar
    from src.utl.write_files import list2file, save_link_grammar
    from src.utl.widgets import html_table, plot2d

    from collections import OrderedDict
    log = OrderedDict({'datime': str(UTC()), 'learn_grammar': '80511'})
    #log.update({'datime': str(UTC()), 'learn_grammar': '80510'})
    files, re01 = check_mst_files(input_parses, verbose)
    log.update(re01)
    #for file in files: copy(file, output_categories)
    #TODO: output_categories file ⇒ dir
    if os.path.isdir(output_categories):
        parse_dir = output_categories + '/parses/'
    else: parse_dir = os.path.dirname(output_categories) + '/parses/'
    if check_dir(parse_dir, True, verbose):
        for file in files: copy(file, os.path.dirname(parse_dir))
    else: raise FileNotFoundError('File not found', input_parses)
    # group = True    #? always? False option for context = 0 (words)?
    kwargs['input_files'] = files
    links, re02 = files2links(**kwargs)
    log.update(re02)
    if verbose == 'debug':
        print('\nfiles2links returns links', type(links), ':\n')
        with pd.option_context('display.max_rows', 6): print(links, '\n')
        print('learn_grammar: word_space:', word_space, '/ clustering:', clustering)

    category_list, re03 = category_learner(links, **kwargs)
    log.update(re03)
    word_clusters = clusters2dict(category_list)
    # Save 1st cats_file = to control 2-step generalization #FIXME:DEL
    cats_file = output_categories
    if '.' not in cats_file:  #80508 auto file name
        if cats_file[-1] != '/': cats_file += '/'
        cats_file += (str(len(set([x[0] for x in category_list]))) + '_categories.txt')
    #TODO: comment saving cats_file and run tests 80523
    #+categories = list2file(category_list, cats_file)
    log.update({'categories_file': cats_file})
    #...TODO... hierarchical categories  80523 snooze
    #...display(html_table([['Code','Parent','Id','Quality','Words','Relevance']] \
    #...        + category_list))

    if grammar_rules != context:
        #-links, res4 = files2links(files, parse_mode, grammar_rules, group, left_wall, period, verbose)
        context = kwargs['context']
        kwargs['context'] = kwargs['grammar_rules']
        links, re04 = files2links(**kwargs)
        kwargs['context'] = context

    rule_list, re05 = grammar_learner(word_clusters, links, **kwargs)
    log.update(re05)
    #...display(html_table([['Rules','','','','','']] + rule_list))

    if 'rules_generalization' in kwargs:
        if kwargs['rules_generalization'] not in ['','off']:
            #-word_clusters, re06 = generalize_rules(rule_list, **kwargs)
            cats_list, re06 = generalise_rules(rule_list, **kwargs)
            #TODO: = generalise_rules(rule_list, **kwargs)
            log.update(re06)
            if len(set([x[0] for x in cats_list])) < len(set([x[0] for x in category_list])):
                category_list = cats_list
                # Save 2nd cats_file - overwrite in case of equal
                cats_file = output_categories
                if '.' not in cats_file:  #80508 auto file name
                    if cats_file[-1] != '/': cats_file += '/'
                    cats_file += (str(len(set([x[0] for x in category_list]))) + '_categories.txt')
                #TODO: comment saving cats_file and run tests 80523
                #+categories = list2file(category_list, cats_file)
                log.update({'categories_file': cats_file})
                word_clusters = clusters2dict(category_list)
                rule_list, re07 = grammar_learner(word_clusters, links, **kwargs)
                #...display(html_table([['Rules','','','','','']] + rule_list))
                log.update(re07)
                if verbose == 'debug':
                    print('\nrules_generalisation ⇒ category_list:', category_list)
    if verbose not in ['min','none']:
        display(html_table([['Code','Parent','Id','Quality','Words','Relevance']] \
            + category_list))

    # Save cat_tree.txt file
    from src.utl.write_files import save_category_tree
    tree_file = cats_file[:cats_file.rindex('_')] + '_cat_tree.txt'
    re08 = save_category_tree(category_list, tree_file, verbose)  #FIXME: verbose?
    log.update(re08)
    # Save Link Grammar .dict
    re09 = save_link_grammar(rule_list, output_grammar)
    log.update(re09)

    return log


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
        prj_dir = batch_dir + '/' + dataset  + '/' + \
            spaces[kwargs['context']-1] + '-'+wtf+'-' + spaces[kwargs['grammar_rules']-1] \
            + '/' + left_wall + '_' + period + '/' + generalization[gen]

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

#def parse_metrics(test_corpus, dict_path, template_path,  ref_path, linkage_limit):
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
    #from link_grammar.lgparse import *
    #from link_grammar.cliutils import *
    #from link_grammar.optconst import *
    #SyntaxError: import * only allowed at module level
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
    from src.grammar_learner.poc04 import parse_metrics
    input_parses, output_categories, output_grammar = \
        params(corpus, dataset, module_path, out_dir, **kwargs)
    #TODO: check out_dir - absolute/relative ⇒ add module_path
    response = learn_grammar(input_parses, output_categories, output_grammar, **kwargs)
    # Category tree
    #-80411 v.0.1:
    #-from src.utl.widgets import category_tree  # 80411
    #-tree = category_tree(response['categories_file'], kwargs['verbose'])
    #-TODO: save category tree in learn_grammar, add path to response
    #tree = category_tree(response['categories_file'], 'max')
    #return tree, response #80411 tree v.0 ⇒ snooze
    #-print('run_learn_grammar - dict_path:', dict_path)
    # Metrics: parse_ability, parse_quality #80515
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
#TODO: hierarchical cat_tree
