import numpy as np
import pandas as pd


def cluster_links_matrix(clusters, word_links):  # 80224 Turtle 4
    cols = ['cluster', 'cluster_words']
    cluster_list = clusters['cluster'].tolist()
    cols.extend(cluster_list)
    matrix = pd.DataFrame(columns=cols)
    matrix[['cluster','cluster_words']] = clusters[['cluster','cluster_words']]
    matrix[cluster_list] = 0
    for row in word_links.itertuples():
        matrix.loc[matrix['cluster']==row[4], row[5]] += row[3]
    matrix[cluster_list] = matrix[cluster_list].astype(int)
    return matrix

def clusters2links(clusters, parses):  # 80224 Turtle 4 [x] 80228 replaced
    cluster_links = parses.groupby(['link']).sum().reset_index()
    cluster_words = {row[1]: row[2] for row in clusters.itertuples()}
    def link2clusters(row):
        x = []
        x.append(cluster_words[row['link'][:3]])
        x.append(cluster_words[row['link'][3:]])
        return x
    def afunction(link):
        x = []
        x.append(cluster_words[link[:3]])
        x.append(cluster_words[link[3:]])
        return x
    cluster_links['linked_clusters'] = cluster_links['link'].apply(afunction)
    linked_clusters = {row[1]: row[3] for row in cluster_links.itertuples()}
    return linked_clusters


def cluster_connectors(clusters, parses):  # 80228 clusters2links replacement
    cluster_links = parses.groupby(['connector']).sum().reset_index()
    cluster_words = {row[1]: row[2] for row in clusters.itertuples()}
    def words(connector):
        x = []
        x.append(cluster_words[connector[:3]])
        x.append(cluster_words[connector[3:]])
        return x
    cluster_links['linked_clusters'] = cluster_links['connector'].apply(words)
    linked_clusters = {row[1]: row[3] for row in cluster_links.itertuples()}
    return linked_clusters
