# language-learning/src/grammar_learner/skl_clustering.py               # 90118
import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans, MeanShift, \
    estimate_bandwidth
# from sklearn import metrics, pairwise_distances
from sklearn.metrics import silhouette_score, calinski_harabaz_score
from sklearn.neighbors import kneighbors_graph
# davies_bouldin_score -- next scikit-learn release?
# https://github.com/scikit-learn/scikit-learn/issues/11303
from .utl import kwa
from .clustering import cluster_id


def skl_clustering(cd, n_clusters=10, **kwargs):
    # cd: ndarray(words*disjuncts)
    clustering = kwa(('agglomerative', 'ward'), 'clustering', **kwargs)
    if type(clustering) is str:
        if clustering == 'kmeans':
            clustering = ('kmeans', 'k-means++', 10)
        elif clustering == 'agglomerative':
            clustering = ('agglomerative', 'ward')
        elif clustering == 'mean_shift':
            clustering = ('mean_shift', 'auto')
        elif clustering == 'group':  # TODO: call ILE clustering?
            return [], {'clustering': 'skl_clustering error',
                        'clustering_error':
                            'ILE grouping not supported in skl_clustering'}, []
        elif clustering == 'random':  # TODO: call random clustering?
            return [], {'clustering': 'skl_clustering error',
                        'clustering_error':
                            'random not supported in skl_clustering'}, []
        else:
            clustering = ('agglomerative', 'ward')
    clustering_metric = kwa(('silhouette', 'euclidean'),
                            'clustering_metric', **kwargs)
    labels = np.asarray([[]])
    metrics = {'clustering': clustering}
    centroids = np.asarray([[]])

    try:  # if True:  #
        if clustering[0] == 'agglomerative':
            linkage = 'ward'
            affinity = 'euclidean'
            connectivity = None
            compute_full_tree = 'auto'
            if clustering[1] in ['average', 'complete', 'single']:
                linkage = clustering[1]
            if len(clustering) > 2:
                if clustering[2] in ['euclidean', 'cosine', 'manhattan']:
                    affinity = clustering[2]
            if len(clustering) > 3:  # connectivity
                if type(clustering[3]) is int and clustering[3] > 0:
                    neighbors = clustering[3]
                    # TODO: int / dict 
                    connectivity = kneighbors_graph(cd, neighbors,
                                                    include_self=False)
            if len(clustering) > 4:  # compute_full_tree
                if clustering[4] is bool:
                    compute_full_tree = clustering[4]

            model = AgglomerativeClustering(
                n_clusters=n_clusters, linkage=linkage, affinity=affinity,
                connectivity=connectivity, compute_full_tree=compute_full_tree)
            model.fit(cd)
            labels = model.labels_

            # TODO: centroids = ...

        elif clustering[0] in ['k-means', 'kmeans']:
            if clustering[1] in ['k-means++']:  # 'random' - fails?
                init = clustering[1]
            else:
                init = 'k-means++'
            if len(clustering) > 2 and type(clustering[2]) is int:
                n_init = clustering[2]
            else:
                n_init = 10
            model = KMeans(init=init, n_clusters=n_clusters, n_init=n_init)
            model.fit(cd)
            labels = model.labels_
            metrics['inertia'] = model.inertia_
            centroids = np.asarray(model.cluster_centers_[:(max(labels) + 1)])

        elif clustering[0] in ['mean shift', 'mean_shift']:
            if len(clustering) < 2:
                bandwidth = None
            if type(clustering[1]) is int:
                bandwidth = clustering[1]
            else:
                bandwidth = None  # TODO: auto ⇒ estimate_bandwidth
            model = MeanShift(bandwidth=bandwidth)
            model.fit(cd)
            labels = model.labels_
            centroids = np.asarray(model.cluster_centers_[:(max(labels) + 1)])

        else:  # TODO: random clustering?
            model = AgglomerativeClustering(linkage='ward',
                                            n_clusters=n_clusters)
            model.fit(cd)
            labels = model.labels_

        try:
            metrics['silhouette_index'] = float(
                silhouette_score(cd, labels, metric=clustering_metric[1]))
        except:
            metrics['silhouette_index'] = 0.0
        try:
            metrics['variance_ratio'] = float(
                calinski_harabaz_score(cd, labels))
        except:
            metrics['variance_ratio'] = 0.0
        # try:
        #   metrics['davies_bouldin_score'] = float(
        #       davies_bouldin_score(cd, labels))
        # except: metrics['davies_bouldin_score'] = 0.0

        return labels, metrics, centroids
    except:  # else:  #
        return [], {'clustering': 'skl_clustering error'}, []


def optimal_clusters(cd, **kwargs):
    # cluster_range = kwa((2,48,1), 'cluster_range')
    algo = kwa('kmeans', 'clustering', **kwargs)
    criteria = kwa('silhouette', 'cluster_criteria', **kwargs)
    level = kwa(1.0, 'cluster_level', **kwargs)
    verbose = kwa('none', 'verbose', **kwargs)
    crange = kwa((2, 50, 2), 'cluster_range', **kwargs)

    if type(algo) is str:
        if algo == 'kmeans':
            algo = ('kmeans', 'k-means++', 10)
        elif algo == 'agglomerative':
            algo = ('agglomerative', 'ward')
        elif algo == 'group':
            return [], {'clustering': 'skl_clustering error',
                        'clustering_error':
                            'ILE grouping not supported in skl_clustering'}, []
        elif algo == 'random':
            return [], {'clustering': 'skl_clustering error',
                        'clustering_error':
                            'ILE grouping not supported in skl_clustering'}, []
        else:
            algo = ('agglomerative', 'ward')

    if type(crange) is int:
        labels, metrics, centroids = skl_clustering(cd, crange, **kwargs)

    if type(crange) in [tuple, list]:
        if len(crange) == 1:
            if type(crange[0]) is int:
                labels, metrics, centroids = skl_clustering(cd, crange[0],
                                                            **kwargs)
        elif len(crange) == 2:
            if type(crange[0]) is int and type(crange[1]) is int:
                labels, metrics, centroids = skl_clustering(cd, crange[0],
                                                            **kwargs)
                for n in range(crange[1] - 1):
                    l, m, c = skl_clustering(cd, crange[0], **kwargs)
                    if m['silhouette_index'] > metrics['silhouette_index']:
                        labels, metrics, centroids = l, m, c
        elif len(crange) == 3:  # TODO: replace with SGD?
            n_min = min(crange[0], crange[1])
            n_max = max(crange[0], crange[1])
            labels, metrics, centroids = \
                skl_clustering(cd, int((n_min + n_max) / 2), **kwargs)
            for n_clusters in range(n_min, n_max + 1):
                for n in range(kwargs['cluster_range'][2]):
                    l, m, c = skl_clustering(cd, n_clusters, **kwargs)
                    if m['silhouette_index'] > metrics['silhouette_index']:
                        labels, metrics, centroids = l, m, c
        elif len(crange) == 4:
            n_min = min(crange[0], crange[1])
            n_max = max(crange[0], crange[1])
            labels, metrics, centroids = \
                skl_clustering(cd, int((n_min + n_max) / 2), **kwargs)
            for n_clusters in range(n_min, n_max + 1, crange[2]):
                for n in range(kwargs['cluster_range'][3]):
                    l, m, c = skl_clustering(cd, n_clusters, **kwargs)
                    if m['silhouette_index'] > metrics['silhouette_index']:
                        labels, metrics, centroids = l, m, c
        else:
            labels, metrics, centroids = skl_clustering(cd, 10, **kwargs)

    return labels, metrics, centroids  # return clusters, silhouette, m2, labels


# Notes:

# from sklearn.metrics import davies_bouldin_score -- next sklearn release?
    # https://github.com/scikit-learn/scikit-learn/issues/11303
# 81107 k-means, mean_shift
# 81203 cleanup
# 90118 cleanup: remove debug printing
