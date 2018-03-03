import numpy as np
import pandas as pd

def dumb_parser(input_file, verbose='none'):    # 80206 POC-Turtle-1
    wps = pd.DataFrame(columns=['word1','word2','count'])
    wps['count'] = wps['count'].astype(int)
    i = 0
    with open(input_file, 'r') as f:
        sentences = f.readlines()
    for j,sentence in enumerate(sentences):
        if len(sentence) > 1:
            #?if sentence[-1] != '.': sentence = sentence + '.'
            sentence = sentence.replace('.', ' .').replace('  ', ' ')
            words = ['###LEFT-WALL###'] + sentence.split()
            for k,word in enumerate(words): # parse: words » links
                if k < len(words)-1 :
                    wps.loc[i] = [words[k], words[k+1], 1]
                    i += 1
        elif verbose == 'max': print('Empty line - EOF?', input_file)
    wps['count'] = wps['count'].astype(int)
    return wps


def dumb_disjuncter(input_file, lw='#LW#', dot=True, verbose='none'):    # 80216 POC-Turtle-3
    #-print('dumb_disjuncter: lw =', lw, 'dot =', dot)
    djs = pd.DataFrame(columns=['word','disjunct','count'])
    djs['count'] = djs['count'].astype(int)
    i = 0
    with open(input_file, 'r') as f: sentences = f.readlines()
    for j,sentence in enumerate(sentences):
        if len(sentence) > 1:
            #?if sentence[-1] != '.': sentence = sentence + '.'
            if dot == True:
                sentence = sentence.replace('.', ' .').replace('  ', ' ')
            else: sentence = sentence.replace('.', '')
            if type(lw) == str and lw != 'none':
                sentence = lw + ' ' + sentence
            #-print(sentence)
            words = sentence.split()
            #-print(words)
            for k,word in enumerate(words):
                #-print(k, word)
                if k == 0: disjunct = words[k+1] + '+'
                else:
                  disjunct = words[k-1] + '-'
                  if k < len(words)-1:
                      disjunct = disjunct + ' & ' + words[k+1] + '+'
                #-print(disjunct)
                djs.loc[i] = [word, disjunct, 1]
                i += 1
        elif verbose == 'max': print('Empty line - EOF?', input_file)
    djs['count'] = djs['count'].astype(int)
    return djs


def parses2vec(parses,path,tmpath,dim=100,cds=1.0,eig=0.5,neg=1,verbose='none'):
    # 802... » 80223 updated » wps2vec
    from .sws import singular_word_space, word_space
    from .hyperwords import epmisvd
    links = singular_word_space(parses, verbose)
    prefix = ''
    words, context, response = word_space(links, path, prefix, verbose)
    if verbose not in ['none','min']:
        print('\nlinks:', len(links), type(links), \
              '\ncontext:', len(context), type(context), \
              '\nwords:', len(words), type(words))
    if verbose == 'max':
        with pd.option_context('display.max_rows', 6): print(words, '\n')
    vectors, res2 = epmisvd(links, path, tmpath, dim, cds, eig, neg, verbose)
    response.update(res2)
    return vectors, response


def dmb_parser(input_file, lw='###LEFT-WALL###', dot=True, verbose='none'):
    # 80220 dumb_parser enhanced
    wps = pd.DataFrame(columns=['word1','word2','count'])
    wps['count'] = wps['count'].astype(int)
    i = 0
    with open(input_file, 'r') as f:
        sentences = f.readlines()
    for j,sentence in enumerate(sentences):
        if len(sentence) > 1:
            if dot == True:
                #?if sentence[-1] != '.': sentence = sentence + '.'
                sentence = sentence.replace('.', ' .').replace('  ', ' ')
            else: sentence = sentence.replace('.', '')
            if type(lw) == str and lw != 'none':
                sentence = lw + ' ' + sentence
            words = sentence.split()
            for k,word in enumerate(words): # parse: words » links
                if k < len(words)-1 :
                    wps.loc[i] = [words[k], words[k+1], 1]
                    i += 1
        elif verbose == 'max': print('Empty line - EOF?', input_file)
    wps['count'] = wps['count'].astype(int)
    return wps  # parses » wps2vec, parses2links 80220-23


def wps2vec(parses,path,tmpath,dim=100,cds=1.0,eig=0.5,neg=1,verbose='none'):
    # 80223 parses2vec enhanced Turtle-4: return + singular values
    # parses - from dmb_parser
    from .sws import singular_word_space, word_space
    from .hyperwords import pmisvd  # ex.epmisvd - changed 80223
    # Create word space: parse ('a','b') » ('a','b+'), ('b','a-')
    links = singular_word_space(parses, verbose)
    prefix = ''
    words, context, response = word_space(links, path, prefix, verbose)
    if verbose not in ['none','min']:
        print('\nlinks:', len(links), type(links), \
              '\ncontext:', len(context), type(context), \
              '\nwords:', len(words), type(words))
    if verbose == 'max':
        with pd.option_context('display.max_rows', 6): print(words, '\n')
    # Create word vectors:
    # dim = 100 # Vector space dimensions
    # cds = 1.0 # Context distribution smoothing [default: 1.0]
    # eig = 0.5 # Weighted exponent of the eigenvalue matrix [default: 0.5]
    # neg = 1   # Number of negative samples; subtracts its log from PMI
    vectors, sv, res2 = pmisvd(links, path, tmpath, dim, cds, eig, neg, verbose)
    # sv - singular values list [float]  # 80223
    response.update(res2)
    return vectors, sv, response


def wps2links(parses, clusters):  # 80224 Turtle-4 [x] 80228 replaced
    # parses - from dmb_parser
    word_clusters = dict()
    for row in clusters.itertuples():
        for word in row[2]: word_clusters[word] = row[1]
    parses['c1'] = parses['word1'].apply(lambda x: word_clusters[x])
    parses['c2'] = parses['word2'].apply(lambda x: word_clusters[x])
    parses['link'] = parses['c1'] + parses['c2']
    return parses  # word_links » link_grammar single_disjuncts


def wps2connectors(parses, clusters):  # 80228 Turtle-4 wps2links replacement
    # parses - from dmb_parser
    word_clusters = dict()
    for row in clusters.itertuples():
        for word in row[2]: word_clusters[word] = row[1]
    connectors = parses.copy()
    connectors['c1'] = connectors['word1'].apply(lambda x: word_clusters[x])
    connectors['c2'] = connectors['word2'].apply(lambda x: word_clusters[x])
    connectors['connector'] = connectors['c1'] + connectors['c2']
    return connectors  # connectors » link_grammar single_disjuncts
