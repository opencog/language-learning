# 80331 POC: Proof of Concepf: Grammar Learner 0.1, POC-English-NoAmb


def number_of_clusters(vdf, cluster_range, algorithm='kmeans', \
                       criteria='silhouette', level=0.9, verbose='none'):
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from IPython.display import display
    from ..utl.turtle import html_table
    from .kmeans import cluster_words_kmeans
    sil_range = pd.DataFrame(
        columns=['Np','Nc','Silhouette','Inertia', 'Cluster words'])
    table = [['N', 'NR', 'Silhouette', 'Inertia', 'Cluster words']]

    # Check number of clusters <= word vector dimensionality
    max_clusters = min(cluster_range[1], len(vdf), max([x for x in list(vdf) if isinstance(x,int)]))

    for i,j in enumerate(range(cluster_range[0], max_clusters, cluster_range[2])):
        cdf, silhouette, inertia = cluster_words_kmeans(vdf, j)
        sil_range.loc[i] = [j, len(cdf), round(silhouette,3), \
            round(inertia,3), cdf['cluster_words'].tolist()]
        table.append([j, len(cdf), round(silhouette,3), round(inertia,3), \
            ' || '.join(' '.join(str(word) for word in cluster) \
                        for cluster in cdf['cluster_words'].tolist())])
    sil_range[['Np','Nc']] = sil_range[['Np','Nc']].astype(int)
    if verbose in ['mid', 'max']:
        print('Silhouette index in a range of cluster numbers')
        plt.plot(sil_range['Np'], sil_range['Silhouette'])
        plt.xlabel('Given clusters number -- K-Means parameter\n')
        plt.ylabel('Silhouette index')
        plt.show()
    if verbose == 'max':
        display(html_table(table))

    if level == 1:
        n_clusters = sil_range.loc[sil_range['Silhouette'].idxmax()]['Nc']
    elif level == 0:
        n_clusters = sil_range.loc[sil_range['Nc'].idxmax()]['Nc']
    else:
        thresh = level * sil_range.loc[sil_range['Silhouette'].idxmax()]['Silhouette']
        if verbose == 'max': print('Threshold at', level, 'max =', round(thresh,3))
        n_clusters = min(sil_range.loc[sil_range['Silhouette'] > thresh]['Nc'].tolist())
    return n_clusters


def clusters2list(clusters):
    categories = []
    for index, row in clusters.iterrows():
        category = []
        category.append('C00')
        category.append(row['cluster'])
        category.append(0.0)
        category.append(row['cluster_words'])
        category.append([0 for x in row['cluster_words']])
        categories.append(category)
    return categories
