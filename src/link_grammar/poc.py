#80405 POC: Proof of Concepf: Grammar Learner 0.1, POC-English-NoAmb
import numpy as np
import pandas as pd


def link_grammar_rules(clusters, links, rules='relaxed', verbose='none'):
    # rules: strict -- AB-&BC+ or AB-&BD+... (lexical entries)
    #        relaxed:  ({A- or B-} & {C+ or D+}) or ({A- or B-} & {C+ or E-})
    #        soft:     ({A- or B-} & {C+ or D+ or E-}) -
    from IPython.display import display
    from ..utl.turtle import html_table

    word_clusters = dict()
    for row in clusters.itertuples():
        for word in row[2]: word_clusters[word] = row[1]
    if verbose == 'max':
        print('word_clusters:\n', word_clusters)

    df = links.copy()
    def link2cluster(link):
        if link[-1] in ['-','+']:
            return word_clusters[link[:-1]] + link[-1]
        else: return word_clusters[link] + '+'
    df['c1'] = df['word'].apply(lambda x: word_clusters[x])
    df['c2'] = df['link'].apply(link2cluster)
    df['disjunct'] = df['c1'] + df['c2']
    if verbose == 'max':
        print('df:\n', df.head(3))

    # if rules == 'soft':  # TODO: snooze
    rulez = dict()
    for row in df.itertuples():
        if row[4] not in rulez: rulez[row[4]] = set()
        rulez[row[4]].add(row[6])
    for k,v in rulez.items():
        rulez[k] = sorted(v)
    if verbose == 'max':
        display(html_table([['Cluster','Rulez']]+[x for x in rulez.items()]))
    #TODO: ... return rule_list - CWLRD

    stalks = dict()
    for row in df.itertuples():
        if row[1] not in stalks: stalks[row[1]] = set()
        stalks[row[1]].add(row[6])
    for k,v in stalks.items():
        stalks[k] = tuple(sorted(v))
    if verbose == 'max':
        display(html_table([['Word','Disjuncts | Stalks']] + \
            [x for x in stalks.items()]))

    multi_stalks = dict()
    #_Need this ... to create Anton's "relaxed" rules
    for k,v in stalks.items():
        #-print(sorted(v))
        if v not in multi_stalks: multi_stalks[v] = set()
        multi_stalks[v].add(k)
    if verbose == 'max':
        display(html_table([['Multi-stalks: Connectors','Germs']] + \
            [x for x in multi_stalks.items()]))

    rules = dict()          #TODO: remove rule_strings, rules_and_words
    rule_strings = dict()   # Grammar-Learner-Clustering.ipynb 80331
    rules_and_words = dict()
    for k,v in multi_stalks.items():
        #-rule = []
        cluster_id = word_clusters[list(v)[0]]
        lefts = [x for x in list(k) if x[-1] == '-']
        rights = [x for x in list(k) if x[-1] == '+']
        if len(lefts) > 0 and len(rights) > 0:
            rule = '{' + ' or '.join(sorted(lefts)) + \
                '} & {' + ' or '.join(sorted(rights)) + '}'
        elif len(lefts) > 0 and len(rights) == 0:
            rule = ' or '.join(sorted(lefts))
        elif len(lefts) == 0 and len(rights) > 0:
            rule = ' or '.join(sorted(rights))
        else:
            rule = ''
        if rule != '':
            if cluster_id not in rules:
                rules[cluster_id] = []
                rule_strings[cluster_id] = '(' + rule + ')'
                rules_and_words[cluster_id] = [[],[]]
            else:
                rule_strings[cluster_id] += (' or (' + rule + ')')
            rules[cluster_id].append(rule)
            rules_and_words[cluster_id][0].append(rule)
            rules_and_words[cluster_id][1].append(list(v))

    if verbose == 'max':
        print('Rules:')  #'\n', rules)
        display(html_table([['Cluster','Rules']] + [x for x in rules.items()]))
        print('\nRule Strings -- rule_strings:')
        display(html_table([['Cluster','Rule_Strings']] + [x for x in rule_strings.items()]))
        print('\nRules and words -- rules_and_words:', rules_and_words)

    #-rule_list.sort()
    #-return rule_list
    return rules  #-dict -- 80330 propotype ⇒ ALT 80331


def save_link_grammar(rules, path, file='', header='', footer=''):  # 80405
    from ..utl.utl import UTC
    if path[-1] != '/': path += '/'
    link_grammar = ''
    line_list = list()
    clusters = set()
    #-if isinstance(rules, dict):    # POC-English 80331 version
    #-elif isinstance(rules, list):  # Turtle backwards compatibility
    #_rules - list: ['cluster', [words], [left djs], [right djs], [stalks]]
    for rule in rules:
        line = ''
        if len(rule[2]) > 0 and len(rule[3]) > 0:
            line += '{' + ' or '.join(str(x) for x in rule[2]) \
                + '} & {' +  ' or '.join(str(y) for y in rule[3]) + '}'
        else:
            if len(rule[2]) > 0:
                line += ' or '.join('('+str(x)+')' for x in rule[2])
            elif len(rule[3]) > 0:
                line += ' or '.join('('+str(x)+')' for x in rule[3])
        if len(rule[4]) > 0:
            if line != '': line += ' or '
            line += ' or '.join('('+str(x)+')' for x in rule[4])

        cluster_number = '% ' + str(rule[0]) + '\n'  # comment line: cluster
        cluster_and_words = ' '.join('"'+word+'"' for word in rule[1]) + ':\n'
        line_list.append(cluster_number + cluster_and_words + line + ';\n')
        clusters.add(rule[0])

    line_list.sort()    #FIXME: overkill?
    nc = str(len(clusters))
    if file != '': out_file = path + file
    else: out_file = path + 'poc-english_'
    out_file = out_file + str(len(clusters)) + 'C_' \
        + str(UTC())[:10] + '_0007.4.0.dict'
    if header == '':
        header = '% POC English Link Grammar v.0.7 ' + str(UTC())
    header = header + '\n' + '<dictionary-version-number>: V0v0v7+;\n' \
        + '<dictionary-locale>: EN4us+;'
    add_rules = 'UNKNOWN-WORD: XXX+;'
    if footer == '':
        footer = '% '+ str(len(clusters)) + ' word clusters, ' \
            + str(len(rules)) + ' Link Grammar rules.\n' \
            + '% Link Grammar file saved to: ' + out_file
    lg = header +'\n\n'+ '\n'.join(line_list) +'\n'+ add_rules +'\n\n'+ footer
    with open (out_file, 'w') as f: f.write(lg)
    return lg


#80331 cloned from .turtle.py ~ 80224 Turtle-4
