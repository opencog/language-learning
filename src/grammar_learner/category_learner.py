# language-learning/src/category_learner.py                             # 81102
import numpy as np
import pandas as pd
from copy import deepcopy
from collections import OrderedDict
from .utl import UTC  # , round1,round2,round3,round4,round5
from .read_files import check_dir  # , check_mst_files
from .hyperwords import vector_space_dim, pmisvd
from .clustering import cluster_id, best_clusters, group_links, random_clusters
from .sparse_word_space import clean_links, co_occurrence_matrix, categorical_distribution
from .skl_clustering import optimal_clusters


def add_disjuncts(cats, links, **kwargs):
    # add disjuncts to categories {cats} after k-means or agglomerative clustering
    # cats: {'cluster': [], 'words': [], }
    fat_cats = deepcopy(cats)
    top_clusters = [i for i, x in enumerate(cats['cluster']) if i > 0 and x is not None]
    # word_clusters = {x:i for i,x in enumerate(top_clusters)}
    word_clusters = dict()  # TODO: ⇒ comprehension?
    for i in top_clusters:
        for word in cats['words'][i]:
            word_clusters[word] = i

    df = links.copy()
    df['cluster'] = df['word'].apply(lambda x: word_clusters[x] if x in word_clusters else 0)
    cdf = df.groupby('cluster').sum().reset_index()
    cdf = cdf.loc[cdf['cluster'] > 0]
    fat_cats['counts'] = [0] + cdf['count'].tolist()

    fat_cats['disjuncts'] = [[]]
    fat_cats['dj_counts'] = [[]]
    cdf = df.groupby(['cluster', 'link'], as_index=False).sum().sort_values(by=['cluster', 'count'],
                                                                            ascending=[True, False])
    for cluster in top_clusters:
        ccdf = cdf.loc[cdf['cluster'] == cluster]
        fat_cats['disjuncts'].append(ccdf['link'].tolist())
        fat_cats['dj_counts'].append(ccdf['count'].tolist())

    fat_cats['djs'] = [[]]
    ldf = df[['link', 'count']].copy().groupby('link').sum().sort_values(by='count', ascending=False).reset_index()
    djdict = {x: i for i, x in enumerate(ldf['link'].tolist())}
    df.drop(['word'], axis=1, inplace=True)
    df['dj'] = df['link'].apply(lambda x: djdict[x])
    cdf = df.groupby(['cluster', 'dj'], as_index=False).sum().sort_values(by=['cluster', 'dj'], ascending=[True, True])
    for cluster in top_clusters:
        ccdf = cdf.loc[cdf['cluster'] == cluster]
        fat_cats['djs'].append(ccdf['dj'].tolist())

    return fat_cats


def learn_categories(links, **kwargs):  # 80802 poc05 restructured learner.py
    # links == pd.DataFrame(columns = ['word', 'link', 'count'])
    def kwa(v, k):
        return kwargs[k] if k in kwargs else v

    cats_file = kwa('/output', 'output_categories')  # to define tmpath
    tmpath = kwa('', 'tmpath')
    parse_mode = kwa('given', 'parse_mode')
    left_wall = kwa('', 'left_wall')
    period = kwa(False, 'period')
    context = kwa(1, 'context')
    window = kwa('mst', 'window')
    weighting = kwa('ppmi', 'weighting')
    # ? distance       = kwa(??,   'distance')
    group = kwa(True, 'group')
    word_space = kwa('vectors', 'word_space')
    dim_max = kwa(100, 'dim_max')
    sv_min = kwa(0.1, 'sv_min')
    dim_reduction = kwa('svm', 'dim_reduction')
    algorithm = kwa('kmeans', 'clustering')  # ⇒ best_clusters
    cluster_range = kwa((2, 50, 2), 'cluster_range')  # ⇒ best_clusters
    cluster_criteria = kwa('silhouette', 'cluster_criteria')
    cluster_level = kwa(0.9, 'cluster_level')
    generalization = kwa('off', 'categories_generalization')
    merge = kwa(0.8, 'categories_merge')
    aggregate = kwa(0.2, 'categories_aggregation')
    grammar_rules = kwa(1, 'grammar_rules')
    verbose = kwa('none', 'verbose')

    log = OrderedDict()
    log.update({'category_learner': '80803-81101'})
    if verbose in ['max', 'debug']:
        print(UTC(), ':: category_learner: word_space/algorithm:', word_space, '/', algorithm)

    if tmpath == '' or tmpath == 'auto':  # temporary files path
        if '.' not in cats_file:
            tmpath = cats_file
        else:
            tmpath = cats_file[:cats_file.rindex('/')]
        if tmpath[-1] != '/': tmpath += '/'
        tmpath += 'tmp/'
        if verbose in ['max', 'debug']:
            print(UTC(), ':: learn_categories: tmpath:', tmpath)
    if check_dir(tmpath, True, verbose):
        log.update({'tmpath': tmpath})
    # TODO:ERROR

    cdf = pd.DataFrame(columns=['cluster', 'cluster_words'])

    # Random Clusters   # 80825
    if algorithm == 'random':
        log.update({'clustering': 'random'})
        cdf = random_clusters(links, **kwargs)

    # «ILE» ?elif word_space[0] in ['d','w']   # d,w: 'discrete'='word_vectors'
    elif algorithm == 'group' or word_space[0] == 'd':  # «ILE»: 'discrete' word_space
        log.update({'clustering': 'ILE'})
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner ⇒ ILE group_links: context =', \
                  str(context) + ', word_space: ' + str(word_space) + ', algorithm:', algorithm)
        cdf = group_links(links, verbose)
        if verbose not in ['min', 'none']:
            print(UTC(), ':: ILE:', len(clusters), 'clusters of identical lexical entries', type(clusters))

    # «DRK» ?if word_space[0] in ['v','e'] or context == 1 or algorithm == 'kmeans':
    elif word_space[0] in ['v', 'e']:  # «DRK» legacy Grammar Learner 0.6
        # word_space :: v,e: 'vectors'='embeddings' | 'discrete', 'sparse'
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner: DRK: context =', str(context) + ',', 'dim_max:', dim_max, ', sv_min:',
                  sv_min, ', word_space: ' + word_space + ', algorithm:', algorithm)
        dict_path = tmpath  # dir to save vectors.txt   # 80420: = tmpath
        try:
            dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        except:
            dim = dim_max
        log.update({'vector_space_dim': dim})
        if verbose in ['mid', 'max', 'debug']:
            print(UTC(), ':: category_learner: vector space dimensionality:', dim, '⇒ pmisvd')
        # -vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        # -vdf, sv, re01 = pmisvd(links, tmpath, tmpath, dim)    # 81021:
        vdf, sv, re01 = pmisvd(links, dict_path, tmpath, dim)
        log.update(re01)
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner: pmisvd ⇒ best_clusters')
        cdf, silhouette, inertia = best_clusters(vdf, **kwargs)
        log.update({'silhouette': silhouette, 'inertia': inertia})

    # Sparse word space, agglomerative clustering 81021, ... ⇒ any clustering
    elif word_space[0] == 's':  # sparse
        log.update({'clustering': 'agglomerative'})
        linx, words, features = clean_links(links, **kwargs)
        print(
            f'{len(links)} links: {len(set(links["word"].tolist()))} unique words, {len(set(links["link"].tolist()))} links')
        print(f'words: len {len(words)}, min {min(words)}, max {max(words)}')
        print(f'features: len {len(features)}, min {min(features)}, max {max(features)}')
        print(f'features: {features}')
        print(f'linx: {linx}')
        counts = co_occurrence_matrix(linx, **kwargs)
        print(f'counts: {counts}')
        cd = categorical_distribution(counts, **kwargs)
        print(f'counts.shape {counts.shape},cd.shape {cd.shape}')

        labels, metrics, centroids = optimal_clusters(cd, **kwargs)  # skl_clustering.py

        print(f'labels: {labels},\n{len(sorted(np.unique(labels)))} unique: {sorted(np.unique(labels))}')

        log.update({'silhouette': metrics['silhouette_index']})
        # labels ⇒ cdf (legacy, extracted from agglomerative_clustering:
        cdf['cluster'] = sorted(np.unique(labels))  # set(labels)
        clusters = {x: [] for x in cdf['cluster'].tolist()}

        for i, x in enumerate(words): clusters[labels[i]].append(x)
        cdf['cluster_words'] = cdf['cluster'].apply(lambda x: clusters[x])
        cdf['cluster'] = range(1, len(cdf) + 1)
        cdf['cluster'] = cdf['cluster'].apply(lambda x: cluster_id(x, len(cdf)))


    else:  # overkill: ILE
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner ⇒ else ⇒ ILE group_links')
        cdf = group_links(links, verbose)
        log.update({'clustering': 'else: ILE'})

    log.update({'n_clusters': len(cdf)})

    print('\ncategory_learner: log:\n', log)

    return cdf2cats(cdf, **kwargs), log  # 81020: cdf2cats


def cats2list(cats):
    # cats == {'cluster':[], 'words':[], ...}
    categories = []
    for i, cluster in enumerate(cats['cluster']):
        category = []
        category.append(cats['cluster'][i])
        category.append(cats['parent'][i])
        category.append(i)
        category.append(round(cats['quality'][i], 2))
        category.append(sorted(cats['words'][i]))
        if 'disjuncts' in cats.keys():
            category.append(sorted(cats['disjuncts'][i]))
        else:
            category.append('no data')
        if 'djs' in cats.keys():
            category.append(sorted(cats['djs'][i]))
        else:
            category.append(' - ')
        category.append(cats['similarities'][i])
        category.append(cats['children'][i])
        categories.append(category)
    return categories


def cdf2cats(clusters, **kwargs):
    # clusters == pd.DataFrame(columns = ['cluster', 'cluster_words', 'disjuncts'])
    cats = {}
    cats['cluster'] = ['A'] + clusters['cluster'].tolist()
    cats['parent'] = [0 for x in cats['cluster']]
    cats['words'] = [[]] + [set(x) for x in clusters['cluster_words'].tolist()]
    if 'disjuncts' in clusters:
        cats['disjuncts'] = [[]] + clusters['disjuncts'].tolist()
        djset = set()
        [[djset.add(y) for y in x] for x in cats['disjuncts']]
        djlist = sorted(djset)
        cats['djs'] = [set([djlist.index(x) for x in y if x in djlist]) for y in cats['disjuncts']]
    if 'counts' in clusters:
        cats['counts'] = [0] + clusters['counts'].tolist()
    if kwargs['word_space'] == 'discrete' or kwargs['clustering'] == 'group':
        cats['quality'] = [1 for x in cats['words']]
        cats['quality'][0] = 0
        cats['similarities'] = [[1 for y in x] for x in cats['words']]
        cats['similarities'][0] = [0]
    else:
        cats['quality'] = [0 for x in cats['words']]
        cats['similarities'] = [[0 for y in x] for x in cats['words']]
    cats['children'] = [0 for x in cats['words']]

    return cats

# Notes:

# 80802 /src/poc05.py restructured ⇒ /src/category_learner.py POC.0.5 80619+80726
# add_disjuncts moved here ⇐ learner.py/learn_grammar
# cats2list moved here ⇐ generalization.py, copied ⇒ poc05.py for legacy compatibility
# group_links moved ⇒ clustering.py
# 80803 clusters, silhouette, inertia = best_clusters(vdf, **kwargs)
# 80825 random clusters ⇒ commit 80828
# 81012 cdf2cats
# 81102 sparse wordspace agglomerative clustering
