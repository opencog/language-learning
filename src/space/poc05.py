#!/usr/bin/env python3
import numpy as np
import pandas as pd
from src.utl.utl import UTC

def corpus_stats(files, extended = False):      #80606
    # files = ['path_to_mst_parse_files', '...', ...]
    from collections import Counter
    words = Counter()
    npw = Counter()     #:non-parsed words
    lefts = Counter()   #:left words in links
    rights = Counter()  #:right words in links
    links = Counter()   #:tuples: (left,right)
    lines = []
    #-n_links = 0
    sentence_lengths = []
    for file in files:
        with open(file, 'r') as f:
            lines.extend(f.readlines())
    for line in lines:
        if(len(line)) > 1:
            x = line.split()
            if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                if x[1] != '###LEFT-WALL###' and x[3] != '.':
                    links[(x[1], x[3])] += 1
                    lefts[x[1]] += 1
                    rights[x[3]] += 1
            elif len(x) > 0:  # sentence:
                sentence_lengths.append(len(x))
                for word in x:
                    if word not in ['###LEFT-WALL###', '.']:
                        if word[0] == '[' and word[-1] == ']':
                            npw[word[1:-1]] += 1    #:non-parsed [words] in sentences
                        else: words[word] += 1      #:parsed words in sentences
    if len(sentence_lengths) > 0:
        asl = int(round(sum(words.values())/len(sentence_lengths),0))
    else: asl = 0
    if len(words) > 0:
        apwc = int(round(sum(words.values())/len(words),0))
    else: apwc = 0
    if len(links) > 0:
        aplc = int(round(sum(links.values())/len(links),0))
    else: aplc = 0
    unpw = set(npw) - set(words)    #:unique non-parsed words
    lost_words = set(words) - (set(lefts)|set(rights))  #:unique words not mentiones in links
    response = {
        'corpus_stats': [
            ['Number of sentences', len(sentence_lengths)],
            ['Average sentence length', asl],
            ['Number of unique parsed words in sentences', len(words)],
            ['Number of unique non-parsed [words] in sentences', len(unpw)],
            ['Total words count in sentences', sum(words.values())],
            ['Non-parsed [words] count in sentences', sum(npw.values())],
            ['Average per-word counts', apwc],
            ['Number of unique links', len(links)],
            ['Total links count', sum(links.values())],
            ['Average per-link count', aplc]
        ],
        'links_stats': {
            'unique_left_words': len(lefts),
            'unique_right_words': len(rights),
            'left_&_right_intersection': len(lefts & rights),
            'left_|_right_union': len(lefts | rights),
            'lost_words': len(lost_words),
            'non_parsed|lost_words': len(unpw | lost_words)
        }
    }
    if extended:
        response.update({'lost_words': lost_words, 'unpw': unpw, 'words': set(words)})
    return response  #endof corpus_stats


def mst2words(input_file, parse_mode='given', context=0, \
              lw='LEFT-WALL', dot=True, verbose='none'):
    #-print(UTC(), 'poc05 mst2words input_file:', input_file)
    pairs = []
    with open(input_file, 'r') as f: lines = f.readlines()
    for line in lines:
        if len(line) > 1:
            if line[0].isdigit():
                x = line.split()
                if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                    if x[1] == '###LEFT-WALL###':
                        if lw in ['', 'none']: continue
                        else: x[1] = lw
                    if not dot and x[3] == '.': continue
                    pairs.append([x[1], x[3]])    # ~1Mlines/s
    df = pd.DataFrame(pairs, columns=['word','link'])
    df['count'] = 1
    return df


def mst2connectors(input_file, parse_mode='given', context=1, \
                   lw='LEFT-WALL', dot=True, verbose='none'):
    #-print(UTC(), 'poc05 mst2connectors')
    df = mst2words(input_file, parse_mode=parse_mode, context=0, \
                    lw=lw, dot=dot, verbose=verbose)
    #_test with singular_word_space - 80329 OK
    #-wps = df.rename(columns={'word':'word1', 'link':'word2'})
    #-from src.space.sws import singular_word_space
    #-links = singular_word_space(wps, "max")
    #_replace singular_word_space:
    lefts = df.copy()
    lefts['word'] = lefts['word'] + '-'
    lefts = lefts.rename(columns={'word':'link', 'link':'word'})
    #-rights = df.copy()
    df['link'] = df['link'] + '+'
    links = pd.concat([lefts, df], axis=0, ignore_index=True)
    #80605: group later:
    #-links = pd.concat([lefts, df], axis=0, ignore_index=True) \
    #-    .groupby(['word','link'], as_index=False).sum() \
    #-    .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
    #-    .reset_index(drop=True)
    if verbose not in ['none', 'min']:
        print('Singular word space links:', len(lefts), 'left words,', \
              len(df), 'right words,', len(links), 'pairs')
    if verbose == 'max':
        with pd.option_context('display.max_rows', 6):
            print('Merged links:\n', links, '\n')
    return links


def mst2disjuncts(input_file, parse_mode='given', context=2, \
                  lw='LEFT-WALL', dot=True, verbose='none'):
    # 80604 updated: PubMed ~149 s / 1917316 unique links word<>disjunct
    #-print(UTC(), 'poc05 mst2disjuncts')
    pairs = []
    links = dict()
    words = dict()

    def save_djs(words,links):  #80604 replace pandas-dataframe-uppend (slow)
        if len(links) > 0:
            for k,v in links.items():
                if len(v) == 1:
                    disjunct = str(list(v)[0])
                else:
                    l = [str(x) for x in v if str(x)[-1] == '-']
                    r = [str(x) for x in v if str(x)[-1] == '+']
                    disjunct = ' & '.join([x for x in (l+r)])
                pairs.append([words[k], disjunct])
        links = dict()
        words = dict()
        return words,links

    with open(input_file, 'r') as f: lines = f.readlines()

    for line in lines:
        if len(line) > 1:
            if line[0].isdigit():
                x = line.split()
                if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                    if x[1] == '###LEFT-WALL###':
                        if lw in ['', 'none']: continue
                        else: x[1] = lw
                    if not dot and x[3] == '.': continue
                    words[x[0]] = x[1]
                    words[x[2]] = x[3]
                    if x[0] not in links:
                        links[x[0]] = set([str(x[3])+'+'])
                    else: links[x[0]].add(str(x[3])+'+')
                    if x[2] not in links:
                        links[x[2]] = set([str(x[1])+'-'])
                    else: links[x[2]].add(str(x[1])+'-')
                else: # sentence starting with digit = same as next else
                    words,links = save_djs(words,links)
            else:  # sentence starting with letter
                words,links = save_djs(words,links)
        else:  # empty line or last LR = same as previous else #80411
            links,words = save_djs(words,links)

    df = pd.DataFrame(pairs, columns=['word','link'])
    df['count'] = 1
    return df


def files2links(**kwargs):  #80426 kwargs  #80605 corpus_stats
    #80406 +TODO: control & limit number of links in disjuncts
    #-print(UTC, 'poc05 files2links: kwargs:\n', kwargs)
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    files = kwargs['input_files']
    parse_mode      = kwa('given',  'parse_mode')
    # parse_mode: 'given'~ as parsed; 'explode' ⇒ maniana...
    left_wall       = kwa('',       'left_wall')
    period          = kwa(False,    'period')
    context         = kwa(1,        'context')
    window          = kwa('mst',    'window')       # not used
    weighting       = kwa('ppmi',   'weighting')    # not used
    #?distance        = kwa(??,   'distance')       # not used
    #?group           = kwa(True,     'group')      # always True?
    group           = True  # always?
    verbose         = kwa('none', 'verbose')
    # Old ideas:
    # level =   0: word pairs: ab » a:b
    #           1: connectors: ab » a:b+, b:a-
    #           2: disjuncts: abc » a:b+, b:a-, b:a-&c+ ...
    #           n>1 disjuncts up to n connectors per germ
    # group = False - don't group - 80323 level=0 case #TODO: DEL group?
    #+from src.space.poc05 import \
    #+    corpus_stats, mst2words, mst2connectors, mst2disjuncts

    corp_stat = corpus_stats(files)     #80606 {} #80605 [[key, value], ...]

    df = pd.DataFrame(columns=['word','link','count'])
    if len(files) == 0:
        return df, {'parsed_links': 0, 'error': 'files2links: files = []'}
    for i,f in enumerate(files):
        if verbose in ['max','debug']:
            print(UTC(),':: src.space.poc05.files2links: File # '+str(i)+':', f)
        if context > 1:
            #-print(UTC(), ':: poc05 files2links - call mst2disjuncts')
            df = pd.concat([df, mst2disjuncts(f, lw=left_wall, dot=period)])
        elif context == 1:
            #-print(UTC(), ':: poc05 files2links - call mst2connectors')
            df = pd.concat([df, mst2connectors(f, lw=left_wall, dot=period)])
        else:
            #-print(UTC(), ':: poc05 files2links - call mst2words')
            df = pd.concat([df, mst2words(f, lw=left_wall, dot=period)])
    parsed_links = len(df)
    if verbose in ['max','debug']:
        print(UTC(),':: src.space.poc05.files2links: parsed_links = len(df) before group:', parsed_links)
    if group:  #Always True  FIXME:?
        df = df.groupby(['word','link'], as_index=False).sum() \
            .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
            .reset_index(drop=True)
    if verbose in ['debug']:
        print(UTC(),':: src.space.poc05.files2links: len(df) after group:', len(df))
    words_number = len(set(df['word'].tolist()))  #TODO: update to 80601 definition
    terms_number = len(set(df['link'].tolist()))  #TODO: update to 80601 definition
    if verbose in ['max','debug']:
        print(UTC(),':: src.space.poc05.files2links:', \
              words_number, 'unique words and', \
              terms_number, 'unique context terms form', \
              len(df),'unique word-term pairs from', \
              parsed_links, 'parsed items.\n Corpus statistics:')
        #display(html_table(re02['corpus_stats'])) #tmp check
        for x in corp_stat['corpus_stats']: print(x[0], ':\t', x[1])

    response = {
        'corpus_stats': corp_stat['corpus_stats'],
        'links_stats' : corp_stat['links_stats'],
        'parsed_links': parsed_links, 'unique_terms': terms_number,
        'unique_words': words_number, 'word-term_pairs': len(df)
    }
    if verbose in ['max','debug']:
        print(UTC(),':: src.space.poc05.files2links: return df, response')
    return df, response


#80322 turtle files2disjuncts ⇒ files2links
#80327 mst2disjuncts = updated src.space.turtle.py
#80331 cleanup
#80406 POC: Proof of Concepf: Grammar Learner 0.1, POC-English-NoAmb
#80406,11 minor updates
#80507 kwargs ⇒ files2links
#80528 poc04 ⇒ poc05
#80601 mst2words pd.df ⇒ pairs []
#80604 mst2disjuncts pd.df ⇒ pairs []
#80605 corpus_stats
