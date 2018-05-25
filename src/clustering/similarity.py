import numpy as np
import pandas as pd
from scipy import spatial

def cosine_similarity(centroids, cluster_words, verbose='none'):
    sim_df = pd.DataFrame(columns=['c1','c2','similarity','c1_words','c2_words'])
    k = 0
    for i in range(len(centroids)):
        c1 = centroids[i]
        for j in range(len(centroids)):
            c2 = centroids[j]
            sim = 1 - spatial.distance.cosine(c1, c2)
            if i < j:
                c1_words = cluster_words[i]
                c2_words = cluster_words[j]
                sim_df.loc[k] = [i, j, sim, c1_words, c2_words]
                k += 1
    sim_df[['c1','c2']] = sim_df[['c1','c2']].astype(int)
    sorted_df = sim_df.sort_values(by=['similarity','c1','c2'], \
        ascending=[False,True,True]) # \
    return sorted_df, {'clusters_similarity_file': 'none'}


def cluster_similarity(clusters_df, verbose='none'):    # 80219,21
    # ++>> check sim = 1 - distance - sure?
    from scipy import spatial
    sim_df = pd.DataFrame(columns=['c1','c2','similarity','c1_words','c2_words'])
    df = clusters_df.copy()
    if 'cluster' in df.columns: del df['cluster']
    if 'cluster_words' in df.columns: del df['cluster_words']
    # TODO? check and delete non-number columns?
    k = 0
    for i in range(len(df)):
        ccv1 = df.iloc[i].tolist()  # cluster centroid vector
        for j in range(i+1, len(df)):
            ccv2 = df.iloc[j].tolist()
            sim = 1 - spatial.distance.cosine(ccv1, ccv2)   # sure?
            if i < j:
                c1 = clusters_df.iloc[i]['cluster']
                c2 = clusters_df.iloc[j]['cluster']
                c1_words = clusters_df.iloc[i]['cluster_words']
                c2_words = clusters_df.iloc[j]['cluster_words']
                sim_df.loc[k] = [c1, c2, sim, c1_words, c2_words]
                k += 1
    #-sim_df[['c1','c2']] = sim_df[['c1','c2']].astype(int)
    if verbose in ['debug']:
        print('cluster_similarity: sim_df:\n', sim_df[['c1','c2', 'similarity']])
    return sim_df.sort_values(by=['similarity','c1','c2'], \
                              ascending=[False,True,True]), \
        {'clusters_similarity_file': 'none'}
