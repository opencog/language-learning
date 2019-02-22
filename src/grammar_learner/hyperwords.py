## Unstructured mess of files from 2017 - TODO: restore the file structure?
from __future__ import division
import logging
import time
import numpy as np
import pandas as pd
#-from collections import Counter
from scipy.sparse import dok_matrix, csr_matrix
from sparsesvd import sparsesvd
import matplotlib.pyplot as plt

'''links => PMI'''

def multiply_by_rows(matrix, row_coefs):
    normalizer = dok_matrix((len(row_coefs), len(row_coefs)))
    normalizer.setdiag(row_coefs)
    return normalizer.tocsr().dot(matrix)

def multiply_by_columns(matrix, col_coefs):
    normalizer = dok_matrix((len(col_coefs), len(col_coefs)))
    normalizer.setdiag(col_coefs)
    return matrix.dot(normalizer.tocsr())

def calc_pmi(counts, cds):  # Calculates e^PMI; PMI without the log().
    sum_w = np.array(counts.sum(axis=1))[:, 0]
    sum_c = np.array(counts.sum(axis=0))[0, :]
    if cds != 1: sum_c = sum_c ** cds   # FIXME: cds = 1.0 ?!
    sum_total = sum_c.sum()
    sum_w = np.reciprocal(sum_w)
    sum_c = np.reciprocal(sum_c)
    pmi = csr_matrix(counts)
    pmi = multiply_by_rows(pmi, sum_w)
    pmi = multiply_by_columns(pmi, sum_c)
    pmi = pmi * sum_total
    return pmi

def save_matrix(f, m):  #_replaced by np.savez... in links2vec
    np.savez_compressed(f, data=m.data, indices=m.indices, indptr=m.indptr, shape=m.shape)
    #-from representations.matrix_serializer import save_matrix:

'''PMI => SVD'''

def load_vocabulary(path):
    with open(path) as f:
        vocab = [line.strip() for line in f if len(line) > 0]
    return dict([(a, i) for i, a in enumerate(vocab)]), vocab

def load_matrix(f):
    if not f.endswith('.npz'):
        f += '.npz'
    loader = np.load(f)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])

class Explicit:
    # Base class for explicit representations.
    # Assumes that the serialized input is e^PMI.
    def __init__(self, path, normalize=True):
        self.wi, self.iw = load_vocabulary(path + '.words.vocab')
        self.ci, self.ic = load_vocabulary(path + '.contexts.vocab')
        self.m = load_matrix(path)
        self.m.data = np.log(self.m.data)
        self.normal = normalize
        if normalize:
            self.normalize()

    def normalize(self):
        m2 = self.m.copy()
        m2.data **= 2
        norm = np.reciprocal(np.sqrt(np.array(m2.sum(axis=1))[:, 0]))
        normalizer = dok_matrix((len(norm), len(norm)))
        normalizer.setdiag(norm)
        self.m = normalizer.tocsr().dot(self.m)

    def represent(self, w):
        if w in self.wi: return self.m[self.wi[w], :]
        else: return csr_matrix((1, len(self.ic)))

    def similarity_first_order(self, w, c):
        return self.m[self.wi[w], self.ci[c]]

    def similarity(self, w1, w2):
        # Assumes the vectors have been normalized.
        return self.represent(w1).dot(self.represent(w2).T)[0, 0]

    def closest_contexts(self, w, n=10):
        # Assumes the vectors have been normalized.
        scores = self.represent(w)
        return heapq.nlargest(n, zip(scores.data, [self.ic[i] for i in scores.indices]))

    def closest(self, w, n=10):
        # Assumes the vectors have been normalized.
        scores = self.m.dot(self.represent(w).T).T.tocsr()
        return heapq.nlargest(n, zip(scores.data, [self.iw[i] for i in scores.indices]))

class PositiveExplicit(Explicit):
    # Positive PMI (PPMI) with negative sampling (neg).
    # Negative samples shift the PMI matrix before truncation.
    def __init__(self, path, normalize=True, neg=1):
        Explicit.__init__(self, path, False)
        self.m.data -= np.log(neg)
        self.m.data[self.m.data < 0] = 0
        self.m.eliminate_zeros()
        if normalize:
            self.normalize()

'''SVD => vectors.txt'''

class Embedding:    # Base class for all embeddings.
                    # SGNS can be directly instantiated with it.
    def __init__(self, path, normalize=True):
        self.m = np.load(path + '.npy')
        if normalize: self.normalize()
        self.dim = self.m.shape[1]
        self.wi, self.iw = load_vocabulary(path + '.vocab')

    def normalize(self):
        norm = np.sqrt(np.sum(self.m * self.m, axis=1))
        self.m = self.m / norm[:, np.newaxis]

    def represent(self, w):
        if w in self.wi: return self.m[self.wi[w], :]
        else: return np.zeros(self.dim)

    def similarity(self, w1, w2):
        # Assumes the vectors have been normalized.
        return self.represent(w1).dot(self.represent(w2))

    def closest(self, w, n=10):
        # Assumes the vectors have been normalized.
        scores = self.m.dot(self.represent(w))
        return heapq.nlargest(n, zip(scores, self.iw))

class SVDEmbedding(Embedding):
    # Enables controlling the weighted exponent of the eigenvalue matrix (eig).
    # Context embeddings can be created with "transpose".
    def __init__(self, path, normalize=True, eig=0.0, transpose=False):
        if transpose:
            print('SVDEmbedding: transpose')    #FIXME:DEL
            ut = np.load(path + '.vt.npy')
            self.wi, self.iw = load_vocabulary(path + '.contexts.vocab')
        else:
            #-print('SVDEmbedding: transpose=False')
            ut = np.load(path + '.ut.npy')
            self.wi, self.iw = load_vocabulary(path + '.words.vocab')
        s = np.load(path + '.s.npy')
        if eig == 0.0:   self.m = ut.T
        elif eig == 1.0: self.m = s * ut.T
        else:            self.m = np.power(s, eig) * ut.T
        self.dim = self.m.shape[1]
        if normalize: self.normalize()

class EnsembleEmbedding(Embedding):
    # Adds the vectors of two distinct embeddings
    # (of the same dimensionality) to create a new representation.
    # Commonly used by adding the context embeddings to the word embeddings.
    def __init__(self, emb1, emb2, normalize=False):
        """ Assume emb1.dim == emb2.dim """
        self.dim = emb1.dim

        vocab1 = emb1.wi.viewkeys()
        vocab2 = emb2.wi.viewkeys()
        joint_vocab = list(vocab1 & vocab2)
        only_vocab1 = list(vocab1 - vocab2)
        only_vocab2 = list(vocab2 - vocab1)
        self.iw = joint_vocab + only_vocab1 + only_vocab2
        self.wi = dict([(w, i) for i, w in enumerate(self.iw)])

        m_joint = emb1.m[[emb1.wi[w] for w in joint_vocab]] \
                  + emb2.m[[emb2.wi[w] for w in joint_vocab]]
        m_only1 = emb1.m[[emb1.wi[w] for w in only_vocab1]]
        m_only2 = emb2.m[[emb2.wi[w] for w in only_vocab2]]
        self.m = np.vstack([m_joint, m_only1, m_only2])

        if normalize: self.normalize()


'''Integrators: link2vec (801), epmisvd (802)'''

def list2tsv(lst, path):
    with open(path, 'w') as f:
        for item in lst: f.write(item + '\n')
    return {'saved_items': len(lst)}

def links2vec(links,out_path,tmp_path,dim=100,cds=1.0,eig=0.5,verbose='none'):
    logger = logging.getLogger(__name__ + ".links2vec")
    #80204: Language Learning - Clustering pipeline January 2018.ipynb
    '''links => PMI'''
    #-cds = 1.0  # cds = float(args['--cds']) # Context distribution smoothing [default: 1.0]
    pmi_path = tmp_path + 'pmi'
    start = time.time()
    #-linkz = links.loc[(links['count'] > 2)]
    linkz = links
    words = linkz.groupby('word').sum().reset_index() \
        .sort_values(by=['count','word'], ascending=[False,True])
    contexts = linkz.groupby('link').sum().reset_index() \
        .sort_values(by=['count','link'], ascending=[False,True])
    # if verbose in ['max','debug']:
    #     print('Linkz:', len(linkz), 'items')
    #     with pd.option_context('display.max_rows', 6): print(linkz)
    #     print('words:', len(words), 'items')
    #     with pd.option_context('display.max_rows', 6): print(words,'\n')
    #     print('contexts:', len(contexts), 'items')
    #     with pd.option_context('display.max_rows', 6): print(contexts)
    logger.info(f'Linkz: {len(linkz)} items')
    with pd.option_context('display.max_rows', 6): logger.info(f"{linkz}")
    logger.info(f'words: {len(words)} items')
    with pd.option_context('display.max_rows', 6): logger.info(f'{words}\n')
    logger.info(f'contexts: {len(contexts)} items')
    with pd.option_context('display.max_rows', 6): logger.info(f"{contexts}")

    iw = sorted(words['word'].drop_duplicates().values.tolist())
    ic = sorted(contexts['link'].drop_duplicates().values.tolist())
    wi = dict([(w, i) for i, w in enumerate(iw)])
    ci = dict([(c, i) for i, c in enumerate(ic)])
    counts = csr_matrix((len(wi), len(ci)), dtype=np.float32)
    tmp_counts = dok_matrix((len(wi), len(ci)), dtype=np.float32)
    update_threshold = 100000   # ~ batch size
    i = 0
    for row in linkz.itertuples():
        if row.word in wi and row.link in ci:
            tmp_counts[wi[row.word], ci[row.link]] = int(row.count)
        i += 1
        if i == update_threshold:
            counts = counts + tmp_counts.tocsr()
            tmp_counts = dok_matrix((len(wi), len(ci)), dtype=np.float32)
            i = 0
    counts = counts + tmp_counts.tocsr()
    list2tsv(iw, pmi_path + '.words.vocab')     # any need to save?
    list2tsv(ic, pmi_path + '.contexts.vocab')
    # if verbose in ['max','debug']: print('PMI data saved to', pmi_path)
    logger.info(f'PMI data saved to {pmi_path}')

    pmi = calc_pmi(counts, cds)
    np.savez_compressed(pmi_path, \
        data=pmi.data, indices=pmi.indices, indptr=pmi.indptr, shape=pmi.shape)
    # if verbose in ['max','debug']:
    #   print('PMI matrix', type(pmi), pmi.shape, '\nsaved to', pmi_path)
    logger.info(f'PMI matrix {type(pmi)}, {pmi.shape}\nsaved to {pmi_path}')

    '''PMI => SVD'''
    svd_path = pmi_path[:-3] + 'svd'
    neg = 1     # int(args['--neg'])  Number of negative samples;
                # [default: 1]        subtracts its log from PMI
    # if verbose in ['max','debug']:
    #   print('SVD started: dim', dim, ', output:', svd_path+'...')
    logger.info(f'SVD started: dim {dim}, output: {svd_path}...')

    explicit = PositiveExplicit(pmi_path, normalize=False, neg=neg)
    ut, s, vt = sparsesvd(explicit.m.tocsc(), dim)
    np.save(svd_path + '.ut.npy', ut)
    np.save(svd_path + '.s.npy', s)
    np.save(svd_path + '.vt.npy', vt)
    list2tsv(explicit.iw, svd_path + '.words.vocab')  # any need to save?
    list2tsv(explicit.ic, svd_path + '.contexts.vocab')
    # if verbose in ['max','debug']:
    #     print('SVD matrix (3 files .npy) saved:', len(ut[0]), 'vectors, ', \
    #         'ut:', len(ut), 's:', len(s), 'vt:', len(vt))
    logger.info(f'SVD matrix (3 files .npy) saved: {len(ut[0])} vectors, ut: {len(ut)}, s: {len(s)}, vt: {len(vt)}')

    '''SVD => vectors.txt'''
    out_file = out_path + 'vectors.txt'
    svd = SVDEmbedding(svd_path, True, eig)
    with open(out_file, 'w') as file:
        for i, w in enumerate(svd.iw):
            file.write(w+' '+(' '.join([str(x) for x in svd.m[i]]))+'\n')
    readme_path = out_path + 'vectors_readme.txt'
    readme = 'Word vectors: dimension '+str(dim)+', '+str(len(svd.iw))+' vectors'
    with open(readme_path, 'w') as f: f.write(readme)
    # if verbose != 'none':
    #     print('vectors saved to\n', out_file, \
    #         '- elapsed', int(round(time.time() - start, 0)), 's ~', \
    #       round((time.time() - start)/len(ut[0])*1000, 3), 'ms/vector')
    logger.warning(f'vectors saved to\n {out_file} - elapsed {int(round(time.time() - start, 0))} s ~ '
                   f'{round((time.time() - start)/len(ut[0])*1000, 3)} ms/vector')

    response = {'vectors_file': out_file}
    return response

def epmisvd(links,path,tmpath,dim=100,cds=1.0,eig=0.5,neg=1,verbose='none'):
    logger = logging.getLogger(__name__ + ".epmisvd")
    # cds = 1.0 # context distribution smoothing [default: 1.0]
    # eig = 0.5 # weighted exponent of the eigenvalue matrix [default: 0.5]
    # neg = 1   # Number of negative samples; [default: 1] subtracts its log from PMI
                # PMI => SVD PositiveExplicit parameter
    '''links => PMI'''
    pmi_path = tmpath + 'pmi'
    start = time.time()
    #-linkz = links.loc[(links['count'] > 2)]
    linkz = links
    words = linkz.groupby('word').sum().reset_index()\
        .sort_values(by=['count','word'], ascending=[False,True])
    contexts = linkz.groupby('link').sum().reset_index()\
        .sort_values(by=['count','link'], ascending=[False,True])
    # if verbose in ['max','debug']:
    #     print('Linkz:', len(linkz), 'items')
    #     with pd.option_context('display.max_rows', 6): print(linkz)
    #     print('words:', len(words), 'items')
    #     with pd.option_context('display.max_rows', 6): print(words,'\n')
    #     print('contexts:', len(contexts), 'items')
    #     with pd.option_context('display.max_rows', 6): print(contexts)
    logger.info(f'Linkz: {len(linkz)} items')
    with pd.option_context('display.max_rows', 6): logger.info(f'{linkz}')
    logger.info(f'words: {len(words)} items')
    with pd.option_context('display.max_rows', 6): logger.info(f'{words}\n')
    logger.info(f'contexts: {len(contexts)} items')
    with pd.option_context('display.max_rows', 6): logger.info(f'{contexts}')

    iw = sorted(words['word'].drop_duplicates().values.tolist())
    ic = sorted(contexts['link'].drop_duplicates().values.tolist())
    wi = dict([(w, i) for i, w in enumerate(iw)])
    ci = dict([(c, i) for i, c in enumerate(ic)])
    counts = csr_matrix((len(wi), len(ci)), dtype=np.float32)
    tmp_counts = dok_matrix((len(wi), len(ci)), dtype=np.float32)
    update_threshold = 100000   # ~ batch size
    i = 0
    for row in linkz.itertuples():
        if row.word in wi and row.link in ci:
            tmp_counts[wi[row.word], ci[row.link]] = int(row.count)
        i += 1
        if i == update_threshold:
            counts = counts + tmp_counts.tocsr()
            tmp_counts = dok_matrix((len(wi), len(ci)), dtype=np.float32)
            i = 0
    counts = counts + tmp_counts.tocsr()
    list2tsv(iw, pmi_path + '.words.vocab')  # any need to save?
    list2tsv(ic, pmi_path + '.contexts.vocab')
    # if verbose in ['max','debug']: print('PMI data saved to', pmi_path)
    logger.info('PMI data saved to' + pmi_path)

    '''counts + vocab => pmi'''
    pmi = calc_pmi(counts, cds)
    np.savez_compressed(pmi_path, \
        data=pmi.data, indices=pmi.indices, indptr=pmi.indptr, shape=pmi.shape)
    # if verbose in ['max','debug']:
    #   print('PMI matrix', type(pmi), pmi.shape, '\nsaved to', pmi_path)
    logger.info(f'PMI matrix {type(pmi)} {pmi.shape}\nsaved to {pmi_path}')

    '''PMI => SVD'''
    svd_path = pmi_path[:-3] + 'svd'
    # if verbose in ['max','debug']:
    #     print('SVD started: dim', dim, ', output:', svd_path+'...')
    logger.info(f'SVD started: dim {dim}, output: {svd_path}...')

    explicit = PositiveExplicit(pmi_path, normalize=False, neg=neg)
    #print('explicit.m:', explicit.m)
    ut, s, vt = sparsesvd(explicit.m.tocsc(), dim)
    np.save(svd_path + '.ut.npy', ut)
    np.save(svd_path + '.s.npy', s)
    np.save(svd_path + '.vt.npy', vt)
    list2tsv(explicit.iw, svd_path + '.words.vocab')  # any need to save?
    list2tsv(explicit.ic, svd_path + '.contexts.vocab')
    # if verbose in ['max','debug']:
    #     print('SVD matrix (3 files .npy) saved:', len(ut[0]), 'vectors, ', \
    #           'ut:', len(ut), 's:', len(s), 'vt:', len(vt))
    logger.info(f'SVD matrix (3 files .npy) saved: {len(ut[0])} vectors, ut: {len(ut)} s: {len(s)} vt:{len(vt)}')

    '''SVD => vectors.txt'''
    svd = SVDEmbedding(svd_path, True, eig)   # TODO: move code here, RAM2RAM
    if len(svd.m[0]) < dim: dim = len(svd.m[0])   # 80216
    vectors_df = pd.DataFrame(columns=['word'] + list(range(1,dim+1)))
    for i, w in enumerate(svd.iw):
        vectors_df.loc[i] = [w] + svd.m[i].tolist()
    out_file = path + 'vectors.txt'
    with open(out_file, 'w') as file:
        for i, w in enumerate(svd.iw):
            file.write(w+' '+(' '.join([str(x) for x in svd.m[i]]))+'\n')
    readme_path = path + 'vectors_readme.txt'
    readme = 'Word vectors: dimension '+str(dim)+', '+str(len(svd.iw))+' vectors'
    with open(readme_path, 'w') as f: f.write(readme)
    # if verbose in ['max','debug']:
    #     print('vectors saved to\n', out_file, \
    #         '- elapsed', int(round(time.time() - start, 0)), 's ~', \
    #       round((time.time() - start)/len(ut[0])*1000, 3), 'ms/vector')
    logger.info(f'vectors saved to\n {out_file} - elapsed {int(round(time.time() - start, 0))} s ~ '
                f'{round((time.time() - start)/len(ut[0])*1000, 3)} ms/vector')

    response = {'vectors_file': out_file}
    return vectors_df, response


def pmisvd(links,path,tmpath, dim=100, cds=1.0, eig=0.5, neg=1, verbose='none'):
    logger = logging.getLogger(__name__ + ".pmisvd")
    '''80223 epmisvd enhanced: return +singular values'''
    # path - dir to save vectors.txt and readme
    # path - dir to save temporary files
    # cds = 1.0 # context distribution smoothing [default: 1.0]
    # eig = 0.5 # weighted exponent of the eigenvalue matrix [default: 0.5]
    # neg = 1   # Number of negative samples; [default: 1] subtracts its log from PMI
                # PMI => SVD PositiveExplicit parameter
    if tmpath[-1] == '/': tmpath = tmpath[:-1]
    if path[-1] == '/': path = path[:-1]

    '''links => PMI'''
    pmi_path = tmpath + '/pmi'
    start = time.time()
    #-linkz = links.loc[(links['count'] > 2)]
    linkz = links
    words = linkz.groupby('word').sum().reset_index()\
        .sort_values(by=['count','word'], ascending=[False,True])
    contexts = linkz.groupby('link').sum().reset_index()\
        .sort_values(by=['count','link'], ascending=[False,True])

    iw = sorted(words['word'].drop_duplicates().values.tolist())
    ic = sorted(contexts['link'].drop_duplicates().values.tolist())
    wi = dict([(w, i) for i, w in enumerate(iw)])
    ci = dict([(c, i) for i, c in enumerate(ic)])
    counts = csr_matrix((len(wi), len(ci)), dtype=np.float32)
    tmp_counts = dok_matrix((len(wi), len(ci)), dtype=np.float32)
    update_threshold = 100000   # ~ batch size
    i = 0
    for row in linkz.itertuples():
        if row.word in wi and row.link in ci:
            tmp_counts[wi[row.word], ci[row.link]] = int(row.count)
        i += 1
        if i == update_threshold:
            counts = counts + tmp_counts.tocsr()
            tmp_counts = dok_matrix((len(wi), len(ci)), dtype=np.float32)
            i = 0
    counts = counts + tmp_counts.tocsr()
    list2tsv(iw, pmi_path + '.words.vocab')  # any need to save?
    list2tsv(ic, pmi_path + '.contexts.vocab')

    '''counts + vocab => pmi'''
    pmi = calc_pmi(counts, cds)
    np.savez_compressed(pmi_path, \
        data=pmi.data, indices=pmi.indices, indptr=pmi.indptr, shape=pmi.shape)

    '''PMI => SVD'''
    svd_path = pmi_path[:-3] + 'svd'
    explicit = PositiveExplicit(pmi_path, normalize=False, neg=neg)
    ut, s, vt = sparsesvd(explicit.m.tocsc(), dim)
    np.save(svd_path + '.ut.npy', ut)
    np.save(svd_path + '.s.npy', s)
    np.save(svd_path + '.vt.npy', vt)
    list2tsv(explicit.iw, svd_path + '.words.vocab')  # any need to save?
    list2tsv(explicit.ic, svd_path + '.contexts.vocab')

    '''SVD => vectors.txt'''
    svd = SVDEmbedding(svd_path, True, eig)   # TODO: move code here, RAM2RAM
    if len(svd.m[0]) < dim: dim = len(svd.m[0])   # 80216
    vectors_df = pd.DataFrame(columns=['word'] + list(range(1,dim+1)))
    for i, w in enumerate(svd.iw):
        vectors_df.loc[i] = [w] + svd.m[i].tolist()
    out_file = path + '/vectors.txt'
    with open(out_file, 'w') as file:
        for i, w in enumerate(svd.iw):
            file.write(w+' '+(' '.join([str(x) for x in svd.m[i]]))+'\n')
    readme_path = path + '/vectors_readme.txt'
    readme = 'Word vectors: dimension '+str(dim)+', '+str(len(svd.iw))+' vectors'
    with open(readme_path, 'w') as f: f.write(readme)

    singular_values = s.tolist()  # type(s): numpy.ndarray
    return vectors_df, singular_values, {'vectors_file': out_file}


def vector_space_dim(links, path, tmpath, dim_max=100, sv_min=0.9,
                     verbose='none', cds=1.0, eig=0.5, neg=1):      # 80329
    vdf, sv, response = pmisvd(links, path, tmpath, dim_max)
    dim = max([i for i,x in enumerate(sv) if x > max(sv)*sv_min])
    return dim+1


# Notes:

# 80329 added vector_space_dim
# TODO: refactor, control disk writes, ... PPMI ⇒ +frequency?
# 90221 minor updates for Grammar Learner tutorial
