# language-learning/src/category_learner.py                             # 90221
import logging
import numpy as np
import pandas as pd
from copy import deepcopy
from collections import OrderedDict, Counter
from .utl import UTC, kwa
from .read_files import check_dir  # , check_mst_files
from .hyperwords import vector_space_dim, pmisvd
from .clustering import cluster_id, best_clusters, group_links, random_clusters
from .sparse_word_space import clean_links, \
    co_occurrence_matrix, categorical_distribution
from .skl_clustering import optimal_clusters


def learn_categories(links, **kwargs):
    """ learns word categories (clusters)
    :param links:   pd.DataFrame(columns = ['word', 'link', 'count'])
    :param kwargs:  disclosed below in kwa(...)
    :return:        (categories, re)
    """
    logger = logging.getLogger(__name__ + ".learn_categories")
    cats_file = kwa('/output', 'output_categories', **kwargs)
    tmpath = kwa('', 'tmpath', **kwargs)
    context = kwa(1, 'context', **kwargs)
    word_space = kwa('embeddings', 'word_space', **kwargs)
    dim_max = kwa(100, 'dim_max', **kwargs)
    sv_min = kwa(0.1, 'sv_min', **kwargs)
    algorithm = kwa('kmeans', 'clustering', **kwargs)
    verbose = kwa('none', 'verbose', **kwargs)

    log = OrderedDict()  # FIXME: log » response
    log.update({'category_learner': 'v.0.7.81231'})

    cdf = pd.DataFrame(columns = ['cluster', 'cluster_words'])

    # Random Clusters
    if algorithm == 'random':
        log.update({'clustering': 'random'})
        cdf = random_clusters(links, **kwargs)

    # «ILE» -- "Identical Lexical Entries"
    elif algorithm == 'group' or word_space[0] == 'd':  # 'discrete' word space
        log.update({'word_space': 'discrete', 'clustering': 'ILE'})
        cdf = group_links(links, **kwargs)

    # «DRK» -- "Dimensionality Reduction (SVD) & K-means clustering"
    elif word_space[0] in ['e', 'v']:  # 'embeddings' / 'vectors' - 0.6 legacy
        dict_path = tmpath
        try:
            dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min,
                                   verbose)
        except:  # FIXME
            dim = dim_max
        log.update({'vector_space_dim': dim})

        vdf, sv, re01 = pmisvd(links, dict_path, tmpath, dim)
        #-log.update(re01)  # {'vectors_file': out_file} -- no need
        cdf, silhouette, inertia = best_clusters(vdf, **kwargs)
        log.update({'silhouette': silhouette, 'inertia': inertia})

    # Sparse word space, agglomerative clustering 2018-10-21, mean shift, ...
    elif word_space[0] == 's':  # 'sparse'
        log.update({'word_space': 'sparse'})
        linx, words, features = clean_links(links, **kwargs)
        log.update({'cleaned_words': len(sorted(np.unique(words))),
                    'clean_features': len(sorted(np.unique(features)))})
        # 'links_array': linx.shape})

        counts = co_occurrence_matrix(linx, **kwargs)
        cd = categorical_distribution(counts, **kwargs)
        labels, metrics, centroids = optimal_clusters(cd, **kwargs)
        # TODO check labels != [] ?  81114 check error via try learn_grammar
        log.update(metrics)

        # labels ⇒ cdf (legacy, extracted from agglomerative_clustering:
        cdf['cluster'] = sorted(np.unique(labels))  # set(labels)
        clusters = {x: [] for x in cdf['cluster'].tolist()}

        for i, x in enumerate(words):
            clusters[labels[i]].append(x)
        cdf['cluster_words'] = cdf['cluster'].apply(lambda x: clusters[x])
        cdf['cluster'] = range(1, len(cdf) + 1)
        cdf['cluster'] = cdf['cluster'].apply(lambda x: cluster_id(x, len(cdf)))

    else:  # random clusters
        cdf = random_clusters(links, **kwargs)
        log.update({'clustering': 'random'})

    if '+' in verbose:
        cluster_sizes = Counter([len(x) for x in cdf['cluster_words'].tolist()])
        log.update(
            {'n_clusters': len(cdf), 'cluster_sizes': dict(cluster_sizes)})

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
    """ transforms DataFrame ⇒ dict (for future hierarchical generalization)
    :param clusters: pd.DataFrame(columns: ['cluster', 'cluster_words', 'disjuncts'])
    :param kwargs:  ['word_space', 'clustering']
    :return:        cats: {'cluster': [], 'words': [[str]], ...]
    """
    cats = {}
    cats['cluster'] = ['A'] + clusters['cluster'].tolist()
    cats['parent'] = [0 for x in cats['cluster']]
    cats['words'] = [[]] + [set(x) for x in clusters['cluster_words'].tolist()]
    if 'disjuncts' in clusters:
        cats['disjuncts'] = [[]] + clusters['disjuncts'].tolist()
        djset = set()
        [[djset.add(y) for y in x] for x in cats['disjuncts']]
        djlist = sorted(djset)
        cats['djs'] = [set([djlist.index(x) for x in y if x in djlist])
                       for y in cats['disjuncts']]
    if 'counts' in clusters:
        cats['counts'] = [0] + clusters['counts'].tolist()

    if ('word_space' in kwargs and kwargs['word_space'] == 'discrete') or \
            ('clustering' in kwargs and kwargs['clustering'] == 'group'):
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
# 81231 cleanup after upstream merge and conflicts resolution (FIXME: 2nd check)
# 90221 tmpath defined in learn, tweaks removed here
# 90410 empty filtered parses dataset issue
