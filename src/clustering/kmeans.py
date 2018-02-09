import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances, silhouette_score

def cluster_kmeans(n_clusters, df, words_list):     # 80209 POC-Turtle-1
    kmeans_model = KMeans(init='k-means++', n_clusters=n_clusters, n_init=10)
    kmeans_model.fit(df)
    labels = kmeans_model.labels_
    inertia  = kmeans_model.inertia_
    centroids = np.asarray(kmeans_model.cluster_centers_)
    silhouette = silhouette_score(df, labels, metric ='euclidean')
    cluster_word_ids = [list() for _ in range(max(labels)+1)]
    cluster_words = [list() for _ in range(max(labels)+1)]
    cluster_sizes = list()
    for i,label in enumerate(labels):
        cluster_word_ids[label].append(i)
        cluster_words[label].append(words_list[i])
    cluster_sizes = [len(c) for c in cluster_words]

    return silhouette, inertia, labels, centroids, \
           cluster_sizes, cluster_word_ids, cluster_words
