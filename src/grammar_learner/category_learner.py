#language-learning/src/category_learner.py  #80802 poc05.py restructured

def add_disjuncts(cats, links, verbose='none'):
    # add disjuncts to categories {dict} after k-means clustering
    # cats: {'cluster': [], 'words': [], }
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


#def category_learner(links, **kwargs):     #80619 POC.0.5 #80726
def learn_categories(links, **kwargs):      #80802 poc05 restructured learner.py
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
    algorithm       = kwa('kmeans', 'clustering')       # ⇒ best_clusters
    cluster_range   = kwa((2,50,2), 'cluster_range')    # ⇒ best_clusters
    cluster_criteria = kwa('silhouette', 'cluster_criteria')
    cluster_level   = kwa(0.9,      'cluster_level')
    generalization  = kwa('off',    'categories_generalization')
    merge           = kwa(0.8,      'categories_merge')
    aggregate       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    verbose         = kwa('none',   'verbose')

    from utl import UTC, round1, round2  #, round3, round4, round5
    from read_files import check_dir #, check_mst_files
    from hyperwords import vector_space_dim, pmisvd
    #+from clustering import number_of_clusters, cluster_words_kmeans, group_links
    from clustering import best_clusters, group_links  #80803 best_clusters
    from write_files import list2file, save_link_grammar

    from collections import OrderedDict
    log = OrderedDict()
    log.update({'category_learner': '80803'})
    if verbose in ['max','debug']:
        print(UTC(),':: category_learner: word_space/algorithm:', word_space, '/', algorithm)

    if tmpath == '' or tmpath == 'auto':  # temporary files path
        if '.' not in cats_file: tmpath = cats_file
        else: tmpath = cats_file[:cats_file.rindex('/')]
        if tmpath[-1] != '/': tmpath += '/'
        tmpath += 'tmp/'
        if verbose in ['max','debug']:
            print(UTC(),':: learn_categories: tmpath:', tmpath)
    if check_dir(tmpath, True, verbose):
        log.update({'tmpath': tmpath})
    #TODO:ERROR

    '''DRK'''   #-if word_space == 'vectors':
    if word_space[0] in ['v','e']: #or context == 1 or algorithm == 'kmeans':
        # word_space options: v,e: 'vectors'='embeddings' | d,w: 'discrete'='word_vectors'
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner: DRK: context =', \
                str(context)+', word_space: '+word_space+', algorithm:', algorithm)
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
    #-if algorithm == 'kmeans':
        #-n_clusters = number_of_clusters(vdf, cluster_range, algorithm,  \
        #-    criteria=cluster_criteria, level=cluster_level, verbose=verbose)
        #-log.update({'n_clusters': n_clusters})
        #-clusters, silhouette, inertia = cluster_words_kmeans(vdf, n_clusters)
        if verbose in ['max','debug']:
            print(UTC(),':: category_learner: ⇒ best_clusters')     #80803
        clusters, silhouette, inertia = best_clusters(vdf, **kwargs)
        log.update({'n_clusters': len(clusters)})
        log.update({'silhouette': silhouette, 'inertia': inertia})

    #?elif type(algorithm) is stringg and algorithm[:5] in ['group','ident']:
    #?elif word_space[0] in ['d','w']   # d,w: 'discrete'='word_vectors'
    else:
        if verbose in ['max', 'debug']:
            print(UTC(),':: category_learner ⇒ ILE group_links: context =', \
                str(context)+', word_space: '+str(word_space)+', algorithm:', algorithm)
        clusters = group_links(links, verbose)
        log.update({'n_clusters': len(clusters)})
        if verbose not in ['min','none']:
            print(UTC(),':: ILE:', len(clusters), \
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
    if word_space == 'vectors' or algorithm == 'kmeans':
        cats['quality'] = [0 for x in cats['words']]
        cats['similarities'] = [[0 for y in x] for x in cats['words']]
    else:
        cats['quality'] = [1 for x in cats['words']]
        cats['quality'][0] = 0
        cats['similarities'] = [[1 for y in x] for x in cats['words']]
        cats['similarities'][0] = [0]
    cats['children'] = [0 for x in cats['words']]

    return cats, log


def cats2list(cats):    #80609
    # cats: {'cluster':[], 'words':[], ...} #80609
    categories = []
    for i,cluster in enumerate(cats['cluster']):
        category = []
        category.append(cats['cluster'][i])
        category.append(cats['parent'][i])
        category.append(i)
        category.append(round(cats['quality'][i],2))
        category.append(sorted(cats['words'][i]))
        if 'disjuncts' in cats.keys():
            category.append(sorted(cats['disjuncts'][i]))
        else: category.append('no data')
        if 'djs' in cats.keys():
            category.append(sorted(cats['djs'][i]))
        else: category.append(' - ')
        category.append(cats['similarities'][i])
        category.append(cats['children'][i])
        categories.append(category)
    return categories


#Notes:

#80802 /src/poc05.py restructured ⇒ /src/category_learner.py POC.0.5 80619+80726
    #add_disjuncts moved here ⇐ learner.py/learn_grammar
    #cats2list moved here ⇐ generalization.py, copied ⇒ poc05.py for legacy compatibility
    #group_links moved ⇒ clustering.py
#80803 clusters, silhouette, inertia = best_clusters(vdf, **kwargs)
#80805
