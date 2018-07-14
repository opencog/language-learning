#!/usr/bin/env python3
import numpy as np
import pandas as pd
from src.utl.utl import UTC

#-def corpus_stats(files, extended = False):      #80606
    # files = ['path_to_mst_parse_files', '...', ...]
def corpus_stats(lines, extended = False):      #80716
    # lines = []
    from collections import Counter
    words = Counter()
    npw = Counter()     #:non-parsed words
    lefts = Counter()   #:left words in links
    rights = Counter()  #:right words in links
    links = Counter()   #:tuples: (left,right)
    #-lines = []        #80714
    #-for file in files:
    #-    with open(file, 'r') as f:
    #-        lines.extend(f.readlines())
    sentence_lengths = []
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


def mst2words(lines, **kwargs):
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    lw  = kwa('', 'left_wall')
    dot = kwa(False, 'period')
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


#-def mst2connectors(input_file, parse_mode='given', context=1, \
#-                   lw='LEFT-WALL', dot=True, verbose='none'):
def mst2connectors(lines, **kwargs):
    #-print(UTC(), 'poc05 mst2connectors')
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    lw  = kwa('', 'left_wall')
    dot = kwa(False, 'period')

    df = mst2words(lines, **kwargs)     #80716
    lefts = df.copy()
    lefts['word'] = lefts['word'] + '-'
    lefts = lefts.rename(columns={'word':'link', 'link':'word'})
    df['link'] = df['link'] + '+'
    links = pd.concat([lefts, df], axis=0, ignore_index=True)
    #80605: group later:
    #-links = pd.concat([lefts, df], axis=0, ignore_index=True) \
    #-    .groupby(['word','link'], as_index=False).sum() \
    #-    .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
    #-    .reset_index(drop=True)
    return links


def mst2disjuncts(lines, **kwargs):
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    lw      = kwa(  '',     'left_wall' )
    dot     = kwa(  False,  'period'    )
    context = kwa(  2,      'context'   )
    pairs = []
    links = dict()
    words = dict()

    def save_djs(words,links):
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


def files2links(**kwargs):  #80426 kwargs  #80605 corpus_stats #80617 lower_case
    #80406 +TODO: control & limit number of links in disjuncts
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    parse_mode      = kwa('lower',  'parse_mode')    # 'casefold' ? #80714
    # parse_mode: 'given'~ as parsed, 'lower', 'casefold', 'explode' ⇒ maniana...
    #-left_wall       = kwa('',       'left_wall')
    #-period          = kwa(False,    'period')
    context         = kwa(2,        'context')
    group           = True  # always? kwa(True,     'group')
    verbose         = kwa('none',   'verbose')
    #?window          = kwa('mst',    'window')     # not used
    #?weighting       = kwa('ppmi',   'weighting')  # not used
    #?distance        = kwa(??,       'distance')   # not used
    #?group           = kwa(True,     'group')      # always True?
    #?group = False - don't group - 80323 level=0 case #TODO: DEL group?
    #TODO? Old ideas:
    #? level =   0: word pairs: ab » a:b
    #?           1: connectors: ab » a:b+, b:a-
    #?           2: disjuncts: abc » a:b+, b:a-, b:a-&c+ ...
    #?           n>1 disjuncts up to n connectors per germ
    #+from src.space.poc05 import \
    #+    corpus_stats, mst2words, mst2connectors, mst2disjuncts
    df = pd.DataFrame(columns=['word','link','count'])

    files = kwargs['input_files']
    #TODO: check file
    if len(files) == 0:
        return df, {'parsed_links': 0, 'error': 'files2links: files = []'}
<<<<<<< HEAD
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
=======

    lines = []
    for i,file in enumerate(files):
        #TODO: check file
        if verbose in ['max','debug']:  print('File # '+str(i)+':', file)
        with open(file, 'r') as f:
            lines.extend(f.readlines())

    if parse_mode == 'lower':
        lines = [' '.join([y.lower() if y != '###LEFT-WALL###' \
            else y for y in x.split() ]) for x in lines]
    elif parse_mode == 'casefold':
        lines = [' '.join([y.casefold() if y != '###LEFT-WALL###' \
            else y for y in x.split() ]) for x in lines]

    corp_stat = corpus_stats(lines)

    if context > 1:
        df = mst2disjuncts(lines, **kwargs)
    elif context == 1:
        df = mst2connectors(lines, **kwargs)
    else:
        df = mst2words(lines, **kwargs)
    parsed_links = len(df)
    if verbose in ['max','debug']:
        print('src.space.poc05 files2links: parsed_links = len(df) before group:', parsed_links)
>>>>>>> lower_case
    if group:  #Always True  FIXME:?
        df = df.groupby(['word','link'], as_index=False).sum() \
            .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
            .reset_index(drop=True)
<<<<<<< HEAD
    if verbose in ['debug']:
        print(UTC(),':: src.space.poc05.files2links: len(df) after group:', len(df))
    words_number = len(set(df['word'].tolist()))  #TODO: update to 80601 definition
    terms_number = len(set(df['link'].tolist()))  #TODO: update to 80601 definition
    if verbose in ['max','debug']:
        print(UTC(),':: src.space.poc05.files2links:', \
=======
    if verbose in ['max','debug']:
        print('src.space.poc05 files2links: len(df) after group:', len(df))
    words_number = len(set(df['word'].tolist()))  #TODO: update to 80601 definition
    terms_number = len(set(df['link'].tolist()))  #TODO: update to 80601 definition

    if verbose in ['max','debug']:                #FIXME:DEL
        print('src.space.poc05 files2links:', \
>>>>>>> lower_case
              words_number, 'unique words and', \
              terms_number, 'unique context terms form', \
              len(df),'unique word-term pairs from', \
              parsed_links, 'parsed items.\n Corpus statistics:')
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
#80714 files2links - to_lower_case
