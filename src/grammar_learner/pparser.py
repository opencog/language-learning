# language-learning/src/grammar_learner/pparser.py                      # 81024
import logging
import pandas as pd
from .corpus_stats import corpus_stats
from .utl import kwa


def mst2words(lines, **kwargs):
    lw = kwa('', 'left_wall', **kwargs)
    dot = kwa(False, 'period', **kwargs)
    pairs = []
    for line in lines:
        if len(line) > 1:
            if line[0].isdigit():
                x = line.split()
                if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                    if x[1] == '###LEFT-WALL###':
                        if lw in ['', 'none']:
                            continue
                        else:
                            x[1] = lw
                    if not dot and x[3] == '.':
                        continue
                    pairs.append([x[1], x[3]])
    df = pd.DataFrame(pairs, columns=['word','link'])
    df['count'] = 1

    return df


def mst2connectors(lines, **kwargs):
    df = mst2words(lines, **kwargs)
    lefts = df.copy()
    lefts['word'] = lefts['word'] + '-'
    lefts = lefts.rename(columns={'word': 'link', 'link': 'word'})
    df['link'] = df['link'] + '+'
    links = pd.concat([lefts, df], axis=0, ignore_index=True, sort=True)

    return links


def mst2disjuncts(lines, **kwargs):
    lw = kwa('', 'left_wall', **kwargs)
    dot = kwa(False, 'period', **kwargs)
    if len(lines[-1]) > 0:
        lines.append([])
    pairs = []
    links = dict()
    words = dict()

    def save_djs(words, links):
        if len(links) > 0:
            for k, v in links.items():
                if k in words:
                    if len(v) == 1:
                        disjunct = words[abs(list(v)[0])] \
                                   + ('+' if list(v)[0] > 0 else '-')
                    else:
                        l = sorted([x for x in v if abs(x) in words and x <= 0],
                                   reverse=True)
                        r = sorted([y for y in v if y in words and y > 0])
                        disjunct = ' & '.join([words[abs(z)]
                                               + ('+' if z > 0 else '-')
                                               for z in (l + r)])
                    pairs.append([words[k], disjunct])
        links = dict()
        words = dict()
        return words, links

    for line in lines:
        if len(line) > 1:
            if line[0].isdigit():
                x = line.split()
                if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                    if x[1] == '###LEFT-WALL###':
                        if lw in ['', 'none']:
                            continue
                        else:
                            x[1] = lw
                    if not dot and x[3] == '.':
                        continue
                    try:
                        i = int(x[0])
                        j = int(x[2])
                    except:
                        continue
                    words[i] = x[1]
                    words[j] = x[3]
                    if i in links:
                        links[i].add(j)
                    else:
                        links[i] = set([j])
                    if j in links:
                        links[j].add(-i)
                    else:
                        links[j] = set([-i])

                else:  # sentence starting with digit = same as next else
                    words, links = save_djs(words, links)
            else:  # sentence starting with letter
                words, links = save_djs(words, links)
        else:  # empty line or last LR = same as previous else
            words, links = save_djs(words, links)

    df = pd.DataFrame(pairs, columns=['word','link'])
    df['count'] = 1

    return df


def files2links(**kwargs):
    logger = logging.getLogger(__name__ + ".files2links")
    parse_mode = kwa('lower',  'parse_mode', **kwargs)    # 'casefold'?
    # parse_mode: 'given'~ as parsed, 'lower', 'casefold', 'explode' ⇒ ...
    context = kwa(2, 'context', **kwargs)
    group = True  # always? » kwa(True, 'group', **kwargs)? FIXME:DEL?
    verbose = kwa('none', 'verbose', **kwargs)
    #?window    = kwa('mst',  'window')    # not used
    #?weighting = kwa('ppmi', 'weighting') # not used
    #?distance  = kwa(??,     'distance')  # not used
    #TODO? Old ideas:
    #? level =   0: word pairs: ab » a:b
    #?           1: connectors: ab » a:b+, b:a-
    #?           2: disjuncts: abc » a:b+, b:a-, b:a-&c+ ...
    #?           n>1 disjuncts up to n connectors per germ

    df = pd.DataFrame(columns=['word', 'link', 'count'])

    files = kwargs['input_files']
    if len(files) == 0:
        return df, {'parsed_links': 0, 'error': 'files2links: files = []'}
    lines = []
    for i, file in enumerate(files):
        # TODO?: check file
        with open(file, 'r') as f:
            lines.extend(f.readlines())

    if parse_mode == 'lower':
        lines = [' '.join([y.lower() if y != '###LEFT-WALL###'
                 else y for y in x.split()]) for x in lines]
    elif parse_mode == 'casefold':
        lines = [' '.join([y.casefold() if y != '###LEFT-WALL###'
                 else y for y in x.split()]) for x in lines]

    response = corpus_stats(lines)
    ordnung = ['word','link','count']
    # wdf = mst2words(lines, **kwargs)[ordnung]
    cdf = mst2connectors(lines, **kwargs)[ordnung]
    ddf = mst2disjuncts(lines, **kwargs)[ordnung]

    unique_connectors = cdf.groupby('link', as_index=False).sum()
    avg_connector_count = round(len(cdf)/len(unique_connectors), 1)
    unique_djs = ddf.groupby('link', as_index=False).sum()
    avg_disjunct_count = round(len(ddf)/len(unique_djs), 1)
    unique_seeds = ddf.groupby(['word', 'link'], as_index=False).sum()
    avg_seed_count = round(len(ddf) / len(unique_seeds), 1)

    ddf['djlen'] = ddf['link'].apply(lambda x: x.count('&') +1)
    avg_disjunct_length = float(round(ddf['djlen'].mean(), 1))
    max_disjunct_length = int(ddf['djlen'].max())

    response['corpus_stats'].extend([
        ['Unique connectors number', len(unique_connectors)],
        ['Total  connectors count ', len(cdf)],
        ['Average connector count ', avg_connector_count],
        ['Unique disjuncts number', len(unique_djs)],
        ['Total  disjuncts count ', len(ddf)],
        ['Average disjunct count ', avg_disjunct_count],
        ['Average disjunct length', avg_disjunct_length],
        ['Maximum disjunct length', max_disjunct_length],
        ['Unique seeds number', len(unique_seeds)],
        ['Total  seeds count ', len(ddf)],
        ['Average seed count ', avg_seed_count]])

    if context > 1:
        df = ddf
        terms = 'disjuncts'
    elif context == 1:
        df = cdf
        terms = 'connectors'
    else:
        df = mst2words(lines, **kwargs)
        terms = 'words'  # legacy, not used  # FIXME:DEL?

    if group:  # Always True?  # FIXME:DEL?
        df = df.groupby(['word','link'], as_index=False).sum() \
            .sort_values(by=['count', 'word', 'link'],
                         ascending=[False, True, True]) \
            .reset_index(drop=True)

    response.update({
        'terms': terms,
        'parsed_links': sum(df['count']),
        'unique_links': len(df),
        'unique_words': len(set(df['word'].tolist())),
        'unique_terms': len(set(df['link'].tolist())),
        'word-term_pairs': len(df.groupby(['word', 'link'],
                                          as_index=False).sum())
    })

    return df, response


# Notes:

# 80725 POC 0.5 restructured - this module was src/space/poc05.py
# 80802 corpus_stats ⇒ corpus_stats.py
# 80829 files2links: Average, max disjunct lengths
# 81024 line 24: cure case of MST parses file last line not ending with CR
# 81231 cleanup
