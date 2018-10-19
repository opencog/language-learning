# Agglomerative clustering POC - development branch                     81012
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
# from sklearn import metrics, pairwise_distances
from sklearn.metrics import silhouette_score, calinski_harabaz_score
from ..grammar_learner.clustering import cluster_id

def agglomerative_clustering(cd, words, n_clusters=10, **kwargs):
    # cd: ndarray(words*disjuncts)
    # words: [x] {id: word}  # legacy compatible: return clusters
    def kwa(v, k):
        return kwargs[k] if k in kwargs else v

    clustering = kwa(('agglomerative', 'ward'), 'clustering')
    # linkage: ('ward', 'average', 'complete')
    # -print(f'agglomerative_clustering: {clustering}')
    cluster_criteria = kwa('silhouette', 'cluster_criteria')  # GL.0.6 legacy
    clustering_metric = kwa(('silhouette', 'euclidean'), 'clustering_metric')
    cdf = pd.DataFrame(columns=['cluster', 'cluster_words'])  # [words]: [str]
    m1 = 0.0
    m2 = 0.0
    centroids = np.asarray([[]])
    if True:  # try:
        if clustering[0] == 'agglomerative':
            # -print(f'agglomerative clustering: {clustering}')
            if clustering[1] in ['ward', 'average', 'complete']:
                linkage = clustering[1]
            else:
                linkage = 'ward'
            model = AgglomerativeClustering(linkage=linkage, n_clusters=n_clusters)
            model.fit(cd)
            labels = model.labels_
            m2 = calinski_harabaz_score(cd, labels)
            centroids = labels  # FIXME

        elif clustering[0] in ['k-means', 'kmeans']:
            # -print(f'k-means clustering: {clustering}')
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
            m2 = model.inertia_
            print(f'k-means inertia: {m2}')
            m2 = calinski_harabaz_score(cd, labels)
            centroids = np.asarray(model.cluster_centers_[:(max(labels) + 1)])
        else:
            # -print(f'else: {clustering}')
            model = AgglomerativeClustering(linkage='ward', n_clusters=n_clusters)
            model.fit(cd)
            labels = model.labels_
            centroids = labels

        # -print(f'labels: {labels}')
        cdf['cluster'] = sorted(np.unique(labels))  # set(labels)
        clusters = {x: [] for x in cdf['cluster'].tolist()}
        for i, x in enumerate(words): clusters[labels[i]].append(x)
        cdf['cluster_words'] = cdf['cluster'].apply(lambda x: clusters[x])
        cdf['cluster'] = range(1, len(cdf) + 1)
        cdf['cluster'] = cdf['cluster'].apply(lambda x: cluster_id(x, len(cdf)))

        # silhouette = metrics.silhouette_score(cd, labels, metric=silhouette_metric)
        if clustering_metric[0] == 'silhouette':
            m1 = silhouette_score(cd, labels, metric=clustering_metric[1])
            # -print(f'clustering_metric: {clustering_metric}')
        elif clustering_metric[0] == 'variance_ratio':  # Calinski-Harabaz Index
            m1 = calinski_harabaz_score(cd, labels)
        # return cdf, silhouette, labels
        return cdf, m1, m2, centroids
    else:  # except:
        return cdf, m1, m2, ['error']