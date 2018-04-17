#80406 POC: Proof of Concepf: Grammar Learner 0.1, POC-English-NoAmb
import numpy as np
import pandas as pd

#80329 dmb_parser replacement:
def mst2words(input_file, parse_mode='given', context=0, \
              lw='LEFT-WALL', dot=True, verbose='none'):
    df = pd.DataFrame(columns=['word','link','count'])
    #?df['count'] = df['count'].astype(float)  # muda?
    i = 0
    with open(input_file, 'r') as f: lines = f.readlines()
    for line in lines:
        if len(line) > 1:
            if line[0].isdigit():
                x = line.split()
                if x[1] == '###LEFT-WALL###':
                    if lw in ['', 'none']: continue
                    else: x[1] = lw
                if not dot and x[3] == '.': continue
                df.loc[i] = [x[1], x[3], 1]
                i += 1
    return df

#80329 singular_word_space replacement:
def mst2connectors(input_file, parse_mode='given', context=1, \
                   lw='LEFT-WALL', dot=True, verbose='none'):
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
    #-links = pd.concat([lefts, rights], axis=0, ignore_index=True) \
    links = pd.concat([lefts, df], axis=0, ignore_index=True) \
        .groupby(['word','link'], as_index=False).sum() \
        .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
        .reset_index(drop=True)
    if verbose not in ['none', 'min']:
        print('Singular word space links:', len(lefts), 'left words,', \
              len(rights), 'right words,', len(links), 'pairs')
    if verbose == 'max':
        with pd.option_context('display.max_rows', 6):
            print('Merged links:\n', links, '\n')
    return links

# 80327
def mst2disjuncts(input_file, parse_mode='given', context=2, \
                  lw='LEFT-WALL', dot=True, verbose='none'):
    df = pd.DataFrame(columns=['word','link','count'])
    i = 0
    links = dict()  #-disjuncts = dict()
    words = dict()
    with open(input_file, 'r') as f: lines = f.readlines()
    #-print(type(lines), len(lines), 'lines[-1]:', lines[-1], 'len(lines[-1]):', len(lines[-1]))
    for line in lines:
        if len(line) > 1:
            if line[0].isdigit():
                x = line.split()
                if x[1] == '###LEFT-WALL###':
                    if lw in ['', 'none']: continue   #80322
                    else: x[1] = lw                   #80322
                if not dot and x[3] == '.': continue  #80322
                words[x[0]] = x[1]
                words[x[2]] = x[3]
                if x[0] not in links:
                    links[x[0]] = set([str(x[3])+'+'])
                else:
                    links[x[0]].add(str(x[3])+'+')
                if x[2] not in links:
                    links[x[2]] = set([str(x[1])+'-'])
                else:
                    links[x[2]].add(str(x[1])+'-')
            else:  # sentence starting with letter
                if len(links) > 0:
                    for k,v in links.items():
                        if len(v) == 1:
                            disjunct = str(list(v)[0])
                        else:
                            l = [str(x) for x in v if str(x)[-1] == '-']
                            r = [str(x) for x in v if str(x)[-1] == '+']
                            disjunct = ' & '.join([x for x in (l+r)])
                        df.loc[i] = [words[k], disjunct, 1]
                        i += 1
                links = dict()
                words = dict()
        else:  # empty line or last LR = same as rpevious else #80411
            if len(links) > 0:
                for k,v in links.items():
                    if len(v) == 1:
                        disjunct = str(list(v)[0])
                    else:
                        l = [str(x) for x in v if str(x)[-1] == '-']
                        r = [str(x) for x in v if str(x)[-1] == '+']
                        disjunct = ' & '.join([x for x in (l+r)])
                    df.loc[i] = [words[k], disjunct, 1]
                    i += 1
            links = dict()
            words = dict()
    return df

#80406 +TODO: control & limit number of links in disjuncts
def files2links(files, parse_mode='given', context=0, group=True, \
                left_wall='', period=False, verbose='none'):
    # from src.space.poc import mst2words, mst2connectors, mst2disjuncts
    # parse_mode: 'given'~ as parsed; 'explode' - TODO
    # level =   0: word pairs: ab » a:b
    #           1: connectors: ab » a:b+, b:a-
    #           2: disjuncts: abc » a:b+, b:a-, b:a-&c+ ...
    #           n>1 disjuncts up to n connectors per germ
    # group = False - don't group - 80323 level=0 case #TODO: DEL group?
    for i,f in enumerate(files):
        if verbose in ['max','debug']:
            print('File # '+str(i)+':', f)
        if i == 0:
            df = pd.DataFrame(columns=['word','link','count'])
        if context > 1:
            df = pd.concat([df, mst2disjuncts(f, lw=left_wall, dot=period)])
        elif context == 1:
            df = pd.concat([df, mst2connectors(f, lw=left_wall, dot=period)])
        else:
            df = pd.concat([df, mst2words(f, lw=left_wall, dot=period)])
    parsed_links = len(df)
    if group:
        df = df.groupby(['word','link'], as_index=False).sum() \
            .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
            .reset_index(drop=True)
    words_number = len(set(df['word'].tolist()))
    links_number = len(set(df['link'].tolist()))
    if verbose not in ['none','min']:
        print(words_number, 'unique words and', \
              links_number, 'unique links form', \
              len(df),'unique word-link pairs from', \
              parsed_links, 'parsed items')
    response = {'parsed_links': parsed_links, 'unique_links': links_number, \
                'unique_words': words_number, 'word-link_pairs': len(df)}
    return df, response


#80322 turtle files2disjuncts ⇒ files2links
#80327 mst2disjuncts = updated src.space.turtle.py
#80331 cleanup
#80406,11 minor updates
