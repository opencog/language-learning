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
