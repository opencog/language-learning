# language-learning/src/category_learner.py                             # 81110
import numpy as np
import pandas as pd
from copy import deepcopy
from collections import OrderedDict, Counter
from .utl import UTC, kwa  # , round1,round2,round3,round4,round5
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
    cats_file = kwa('/output', 'output_categories', **kwargs)  # to define tmpath
    tmpath = kwa('', 'tmpath', **kwargs)
    context = kwa(1, 'context')
    word_space = kwa('vectors', 'word_space', **kwargs)
    dim_max = kwa(100, 'dim_max', **kwargs)
    sv_min = kwa(0.1, 'sv_min', **kwargs)
    algorithm = kwa('kmeans', 'clustering', **kwargs)  # ⇒ best_clusters
    verbose = kwa('none', 'verbose', **kwargs)

    log = OrderedDict()
    log.update({'category_learner': '80803-81110'})
    if verbose in ['max', 'debug']:
        print(UTC(), ':: category_learner: word_space/algorithm:', word_space, '/', algorithm)

    if tmpath == '' or tmpath == 'auto':
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

    # Random Clusters
    if algorithm == 'random':
        log.update({'clustering': 'random'})
        cdf = random_clusters(links, **kwargs)

    # «ILE» ?elif word_space[0] in ['d','w']   # d,w: 'discrete'='word_vectors'
    elif algorithm == 'group' or word_space[0] == 'd':  # «ILE»: 'discrete' word_space
        log.update({'clustering': 'ILE'})
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner ⇒ ILE group_links: context =',
                  str(context) + ', word_space: ' + str(word_space) + ', algorithm:', algorithm)
        cdf = group_links(links, verbose)

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
        vdf, sv, re01 = pmisvd(links, dict_path, tmpath, dim)
        log.update(re01)
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner: pmisvd ⇒ best_clusters')
        cdf, silhouette, inertia = best_clusters(vdf, **kwargs)
        log.update({'silhouette': silhouette, 'inertia': inertia})

    # Sparse word space, agglomerative clustering 81021, ... ⇒ any clustering
    elif word_space[0] == 's':  # sparse
        log.update({'word_space': 'sparse'})
        linx, words, features = clean_links(links, **kwargs)
        if verbose in ['max', 'debug']:
            print(f'{len(links)} links: {len(set(links["word"].tolist()))} unique words, {len(set(links["link"].tolist()))} links')
            print(f'words: len {len(words)}, min {min(words)}, max {max(words)}')
            print(f'features: len {len(features)}, min {min(features)}, max {max(features)}')
            print(f'features: {features}')
            print(f'linx: {linx}')

        counts = co_occurrence_matrix(linx, **kwargs)
        if verbose in ['max', 'debug']:
            print(f'counts: {counts}')
        cd = categorical_distribution(counts, **kwargs)
        if verbose in ['max', 'debug']:
            print(f'counts.shape {counts.shape},cd.shape {cd.shape}')
        labels, metrics, centroids = optimal_clusters(cd, **kwargs)  # skl_clustering.py

        # TODO check labels != [] ?  81114 check error via try learn_grammar

        if verbose in ['max', 'debug']:
            print(
                f'\nlearn_categories ⇒ labels: {labels},\n{len(sorted(np.unique(labels)))} unique: {sorted(np.unique(labels))}')

        log.update(metrics)
        # labels ⇒ cdf (legacy, extracted from agglomerative_clustering:
        cdf['cluster'] = sorted(np.unique(labels))  # set(labels)
        clusters = {x: [] for x in cdf['cluster'].tolist()}

        for i, x in enumerate(words): clusters[labels[i]].append(x)
        cdf['cluster_words'] = cdf['cluster'].apply(lambda x: clusters[x])
        cdf['cluster'] = range(1, len(cdf) + 1)
        cdf['cluster'] = cdf['cluster'].apply(lambda x: cluster_id(x, len(cdf)))

    else:  # random clusters
        if verbose in ['max', 'debug']:
            print(UTC(), ':: category_learner ⇒ else ⇒ random clusters')
        cdf = random_clusters(links, **kwargs)
        log.update({'clustering': 'random'})

    cluster_sizes = Counter([len(x) for x in cdf['cluster_words'].tolist()])
    log.update({'n_clusters': len(cdf), 'cluster_sizes': cluster_sizes})

    if verbose in ['max', 'debug']:
        print('\ncategory_learner: log:\n', log)
    return cdf2cats(cdf, **kwargs), log


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
