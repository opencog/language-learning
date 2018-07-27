#!/usr/bin/env python3
#language-learning/src/graammar_learner/pparser.py  #80726
import numpy as np
import pandas as pd

def corpus_stats(lines, extended = False):  #80716 #TODO: 80718 enhance issue
    # lines = []
    from collections import Counter
    words = Counter()
    npw = Counter()     #:non-parsed words
    lefts = Counter()   #:left words in links
    rights = Counter()  #:right words in links
    links = Counter()   #:tuples: (left,right)

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
    lost_words = set(words) - (set(lefts)|set(rights))  #:unique words not mentioned in links
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


def mst2words(lines, **kwargs):         #80717
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    lw  = kwa('', 'left_wall')
    dot = kwa(False, 'period')
    pairs = []
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
    return df  #endof mst2words


def mst2connectors(lines, **kwargs):    #80716
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    lw  = kwa('', 'left_wall')
    dot = kwa(False, 'period')
    df = mst2words(lines, **kwargs)
    lefts = df.copy()
    lefts['word'] = lefts['word'] + '-'
    lefts = lefts.rename(columns={'word':'link', 'link':'word'})
    df['link'] = df['link'] + '+'
    links = pd.concat([lefts, df], axis=0, ignore_index=True, sort=True)
    #80605: group later?:
    #-links = pd.concat([lefts, df], axis=0, ignore_index=True) \
    #-    .groupby(['word','link'], as_index=False).sum() \
    #-    .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
    #-    .reset_index(drop=True)
    return links


def mst2disjuncts(lines, **kwargs):     #80717 +80726 debug dILEd case (lost LW)
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    lw      = kwa(  '',     'left_wall' )
    dot     = kwa(  False,  'period'    )
    context = kwa(  2,      'context'   )
    pairs = []
    links = dict()
    words = dict()
    def save_djs(words,links):
        if kwargs['verbose'] in ['debug']:
            print('save_djs: words, links:', words, links)
        if len(links) > 0:
            for k,v in links.items():
                if k in words:
                    if len(v) == 1:
                        disjunct = words[abs(list(v)[0])] + ('+' if list(v)[0]>0 else '-')
                    else:
                        l = sorted([x for x in v if abs(x) in words and x <= 0], reverse=True)
                        r = sorted([x for x in v if x in words and x > 0])
                        disjunct = ' & '.join([words[abs(x)] + ('+' if x>0 else '-') \
                                               for x in (l+r)])
                    pairs.append([words[k], disjunct])
                    if kwargs['verbose'] in ['debug']: print('pairs:', pairs)
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
                    try:
                        i = int(x[0])
                        j = int(x[2])
                    except: continue
                    words[i] = x[1]
                    words[j] = x[3]
                    if i in links:
                        links[i].add(j)
                    else: links[i] = set([j])
                    if j in links:
                        links[j].add(-i)
                    else: links[j] = set([-i])
                    if kwargs['verbose'] in ['debug']:
                        print('line, words, links:', line, words, links)
                else: # sentence starting with digit = same as next else
                    words,links = save_djs(words,links)
            else:  # sentence starting with letter
                words,links = save_djs(words,links)
        else:  # empty line or last LR = same as previous else #80411
            words,links = save_djs(words,links)

    df = pd.DataFrame(pairs, columns=['word','link'])
    df['count'] = 1

    return df


def files2links(**kwargs):
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

    df = pd.DataFrame(columns=['word','link','count'])

    files = kwargs['input_files']
    #TODO: check file
    if len(files) == 0:
        return df, {'parsed_links': 0, 'error': 'files2links: files = []'}

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

    if group:  #Always True?  #FIXME:?
        df = df.groupby(['word','link'], as_index=False).sum() \
            .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
            .reset_index(drop=True)

    words_number = len(set(df['word'].tolist()))  #TODO: update to 80618 definition
    terms_number = len(set(df['link'].tolist()))  #TODO: update to 80618 definition

    response = {
        'corpus_stats': corp_stat['corpus_stats'],
        'links_stats' : corp_stat['links_stats'],
        'parsed_links': parsed_links, 'unique_terms': terms_number,
        'unique_words': words_number, 'word-term_pairs': len(df)
    }

    return df, response


#80331 cleanup
#80406 POC: Proof of Concepf: Grammar Learner 0.1, POC-English-NoAmb
#80507 kwargs ⇒ files2links
#80528 poc04 ⇒ poc05
#80601 mst2words pd.df ⇒ pairs []
#80604 mst2disjuncts pd.df ⇒ pairs []
#80605 corpus_stats
#80714 files2links - to_lower_case
#80716 conflicts - manual cleanup
#80717 update, 80718 commit from 94..server
#80725 POC 0.1-0.4 deleted, 0.5 restructured - this module was src/space/poc05.py
