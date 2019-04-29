# language-learner/src/grammar_learner/sparse_word_space.py             # 81114
import numpy as np
import pandas as pd
from .utl import kwa


def clean_links(links, **kwargs):
    # links == pd.DataFrame ['word', 'word- & word+']
    min_word_count = kwa(1, 'min_word_count', **kwargs)
    min_link_count = kwa(1, 'min_link_count', **kwargs)
    min_word_frequency = kwa(0.0, 'min_word_frequency', **kwargs)
    min_link_frequency = kwa(0.0, 'min_word_frequency', **kwargs)
    max_words = kwa(1000000, 'max_words', **kwargs)  # SVS: max space dimension 1
    max_features = kwa(1000000, 'max_features', **kwargs)  # SVS: dimension 2: disjuncts/connectors
    # trash = ['.', ',', '+', '-', '?', ':', ';', '!', '"', '{', '}', '|','[', ']', '(', ')', ')(', ')(,', ', ']  # $,&,'
    trash = []  # 81226 FIXME: return
    stop_words = kwa(trash, 'stop_words', **kwargs)

    wdf = links.groupby('word', as_index=False).sum() \
        .sort_values(by=['count', 'word'], ascending=[False, True])
    if 'djlen' in wdf: del wdf['djlen']
    words = np.asarray([x for x in wdf.loc[wdf['count'] > min_word_count - 1]['word']
                       .tolist() if x not in stop_words])
    word_idx = {word: i for i, word in enumerate(words)}

    ldf = links.groupby('link', as_index=False).sum()\
        .sort_values(by=['count', 'link'], ascending=[False, True])
    if 'djlen' in ldf: del ldf['djlen']
    ldf.index = [x for x in range(len(ldf))]
    if kwargs['context'] == 1:
        features = np.asarray(
            [x for x in ldf.loc[ldf['count'] > min_link_count - 1]['link']
                .tolist() if x[:-1] in word_idx])
    else:
        features = np.asarray(ldf.loc[ldf['count'] > min_link_count - 1]['link'].tolist())

    feat_idx = {feature: i for i, feature in enumerate(features)}

    df = links.copy()
    if 'djlen' in df: del df['djlen']
    df['word_id'] = df['word'].apply(lambda x: word_idx[x] if x in word_idx else -1)
    df['feat_id'] = df['link'].apply(lambda x: feat_idx[x] if x in feat_idx else -1)
    if 'word' in df: del df['word']
    if 'link' in df: del df['link']
    df = df.loc[(df['word_id'] > -1) & (df['feat_id'] > -1)] \
        [['word_id', 'feat_id', 'count']]

    return df.values, words, features  # <numpy.ndarray>


def co_occurrence_matrix(linx, **kwargs):  # updated 81012
    # linx == numpy.ndarray [[word_id, feature_id, count]]
    threshold = kwa(1, 'min_co-occurrence_count', **kwargs)
    counts = np.zeros((max(linx[:, 0]) + 1, max(linx[:, 1]) + 1), dtype=np.int16)
    for x in linx: counts[x[0], x[1]] = x[2] if x[2] >= threshold else 0
    return counts


def categorical_distribution(counts, **kwargs):
    # counts: numpy.ndarray [words]*[links]
    threshold = kwa(0.0, 'min_co-occurrence_frequency', **kwargs)
    vsm = np.divide(counts, np.sum(counts))  # Vector Space Model
    cd = (vsm > threshold).astype(int)  # categorical distribution
    return cd
