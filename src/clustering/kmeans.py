import numpy as np
import pandas as pd
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


def cluster_words_kmeans(words_df, n_clusters):     # 80219 POC-Turtle-4
    # 80219 update cluster_kmeans 80209: dataframes, in and out
    from sklearn.cluster import KMeans
    from sklearn.metrics import pairwise_distances, silhouette_score
    words_list = words_df['word'].tolist()
    df = words_df.copy()
    del df['word']
    kmeans_model = KMeans(init='k-means++', n_clusters=n_clusters, n_init=10)
    kmeans_model.fit(df)
    labels = kmeans_model.labels_
    inertia  = kmeans_model.inertia_
    centroids = np.asarray(kmeans_model.cluster_centers_[:(max(labels)+1)])
    silhouette = silhouette_score(df, labels, metric ='euclidean')

    cdf = pd.DataFrame(centroids)
    cdf = cdf.applymap(lambda x: x if abs(x) > 1e-12 else 0.)
    cdf.columns = [x+1 if type(x)==int else x for x in cdf.columns]
    cols = cdf.columns.tolist()
    def cluster_word_list(i):
        return [words_list[j] for j,x in enumerate(labels) if x==i]
    cdf['cluster'] = cdf.index
    cdf['cluster_words'] = cdf['cluster'].apply(cluster_word_list)
    #+cdf = cdf.sort_values(by=[1,2,3], ascending=[True,True,True])
    cdf = cdf.sort_values(by=[1,2], ascending=[True,True])
    cdf.index = range(1, len(cdf)+1)
    def cluster_id(row): return 'C' + str(row.name).zfill(2)
    cdf['cluster'] = cdf.apply(cluster_id, axis=1)
    cols = ['cluster', 'cluster_words'] + cols
    cdf = cdf[cols]

    return cdf, silhouette, inertia
