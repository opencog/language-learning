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

def parses2vec(parses,path,tmpath,dim=100,cds=1.0,eig=0.5,neg=1,verbose='none'):
    from .sws import singular_word_space, word_space
    from .hyperwords import epmisvd
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
    vectors, res2 = epmisvd(links, path, tmpath, dim, cds, eig, neg, verbose)
    response.update(res2)
    return vectors, response

def dumb_disjuncter(input_file, lw='#LW#', dot=True, verbose='none'):    # 80216 POC-Turtle-3
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
                sentence = '#LW# ' + sentence
            #-print(sentence)
            words = sentence.split()
            #-print(words)
            for k,word in enumerate(words):
                #-print(k, word)
                if k == 0: disjunct = ''
                else: disjunct = words[k-1] + '-'
                if k < len(words)-1:
                    disjunct = disjunct + words[k+1] + '+'
                #-print(disjunct)
                djs.loc[i] = [word, disjunct, 1]
                i += 1
        elif verbose == 'max': print('Empty line - EOF?', input_file)
    djs['count'] = djs['count'].astype(int)
    return djs
