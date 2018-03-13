import numpy as np
import pandas as pd


def single_disjuncts(word_links):  # 80228 Turtle-4+
    # word_links - from space/turtle.py/parses2links
    # TODO? update: word_links = connectors from wps2connectors - 80228 update
    if 'connector' in word_links.columns:  # 80228 update compatibility
        word_links = word_links.rename(columns={'connector': 'link'})
    lefts = word_links.loc[:,['word2']]
    lefts['disjunct'] = word_links['link'].apply(lambda x: x + '-')
    rights = word_links.loc[:,['word1']]
    rights['disjunct'] = word_links['link'].apply(lambda x: x + '+')
    lefts = lefts.rename(columns={'word2': 'word'})
    rights = rights.rename(columns={'word1': 'word'})
    word_links_df = pd.concat([lefts, rights])
    word_links_df['count'] = 1
    word_djs_df = word_links_df.groupby(['word','disjunct']).sum().reset_index()
        #-.sort_values(by=['word','disjunct'], ascending=[True,True])
    word_djs = dict()
    for row in word_djs_df.itertuples():
        if row[1] not in word_djs: word_djs[row[1]] = []
        word_djs[row[1]].append(row[2])
    for value in word_djs.values(): value.sort()
    return word_djs  # stalks »


def link_grammar_rules(stalks):  # 80224 Turtle-4
    disjuncts = dict()
    for word,connectors in stalks.items():
        lefts = [x for x in connectors if (('-' in x) and ('+' not in x))]
        rights = [x for x in connectors if (('+' in x) and ('-' not in x))]
        stalks = [x for x in connectors if (('+' in x) and ('-' in x))]
        lefts.sort()
        rights.sort()
        stalks.sort()
        djtuple = (tuple(lefts), tuple(rights), tuple(stalks))
        if djtuple not in disjuncts: disjuncts[djtuple] = set()
        disjuncts[djtuple].add(word)
    rule_list = list()
    for key,words in disjuncts.items():
        rule = []
        if len(list(key[0])) > 0: cluster_id = list(key[0])[0][3:6]
        elif len(list(key[1])) > 0: cluster_id = list(key[1])[0][0:3]
        else: cluster_id = ''
        # TODO: rules for stalks - 3rd list [A- & B+]
        rule.append(cluster_id)
        rule.append(list(words))
        rule.append(list(key[0]))
        rule.append(list(key[1]))
        rule.append(list(key[2]))
        rule_list.append(rule)
    rule_list.sort()
    return rule_list


def save_link_grammar(rule_list, path, file='', header='', footer=''):  # 80307
    # 80307 v.0.6 = updated 80224 version 0.5
    from ..utl.utl import UTC
    # lg_rule_list: ['cluster', [words], [left djs], [right djs], [stalks]]
    link_grammar = ''
    line_list = list()
    clusters = set()
    for rule in rule_list:
        line = ''
        if len(rule[2]) > 0 and len(rule[3]) > 0:
            line += '(' + ' or '.join(str(x) for x in rule[2]) \
                + ') & (' +  ' or '.join(str(y) for y in rule[3]) + ')'
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
    line_list.sort()  # overkill? :)
    nc = str(len(clusters))
    if file != '': out_file = path + file
    else: out_file = path + 'poc-turtle_'
    out_file = out_file + str(len(clusters)) + 'C_' \
        + str(UTC())[:10] + '_0006.4.0.dict'
    if header == '':
        header = '% POC Turtle Link Grammar v.0.6 ' + str(UTC())
    header = header + '\n' + '<dictionary-version-number>: V0v0v6+;\n' + \
        '<dictionary-locale>: EN4us+;'  # 80307
    if footer == '':
        footer = '% '+ str(len(clusters)) + ' word clusters, ' \
            + str(len(rule_list)) + ' Link Grammar rules.\n' \
            + '% Link Grammar file saved to: ' + out_file
    link_grammar = header +'\n\n'+ '\n'.join(line_list) +'\n'+ footer
    with open (out_file, 'w') as f: f.write(link_grammar)
    return link_grammar


def merge_clusters(threshold, n, clusters, sim_df):  # 80224 Turtle-4 FIXME!
    # 80224 Turtle 4 stub TODO: update clustering with threshold and n_cls
    categories = pd.DataFrame(columns=['cluster', 'cluster_words'])
    if n == 5: alist = [['C06', 'C08'], ['C07'], ['C01'], ['C02'], ['C05']]
    elif n == 4: alist = [['C06', 'C08', 'C07'], ['C01'], ['C02'], ['C05']]
    elif n == 3: alist = [['C06', 'C08', 'C07'], ['C01', 'C02'], ['C05']]
    elif n == 2: alist = [['C06', 'C08', 'C07', 'C05'], ['C01', 'C02']]
    else: alist = [['C01'], ['C02'], ['C03'], ['C04'], ['C05'], ['C06']]
    cluster_words = {row[1]: row[2] for row in clusters.itertuples()}
    for i,blist in enumerate(alist):
        category = 'C' + str(n) + str(i+1)
        category_words = []
        for cluster_id in blist: category_words.extend(cluster_words[cluster_id])
        categories.loc[i] = [category, category_words]
    return categories


def merged_clusters_grammar(threshold, n, clusters, sim_df, prs, path):  # 80224
    # 80224 Turtle-4, threshold (0.0-1.0) not used
    from IPython.display import display
    from ..utl.turtle import html_table
    from ..space.turtle import wps2links, wps2connectors
    categories = merge_clusters(threshold, n, clusters, sim_df)
    print(str(len(categories))+' word categories (merged word clusters):')
    display(html_table([['Category', 'Category words']] + categories.values.tolist()))
    lg = link_grammar_rules(single_disjuncts(wps2links(prs, categories)))
    print(str(len(lg)) + ' Link Grammar rules:')
    display(html_table([['Category','Words','Left disjuncts','Right disjuncts','Stalks']] + lg))
    lg_file_string = save_link_grammar(lg, path)
    for line in lg_file_string.splitlines()[-2:]: print(line[2:])
    return lg


def merge_disjunct_germs(df):  # 80303 Turtle-5
    # df columns: 'germs':[], 'disjuncts':[], 'counts':int
    df2 = df.copy()
    if 'count' in df2.columns and 'counts' not in df2.columns:
        #-print('"count" in df2.columns and "counts" not in df2.columns')
        df2.rename(columns={'count': 'counts'})  # fails?!
    df2['disjuncts'] = df2['disjuncts'].apply(lambda x: tuple(sorted(x)))
    if 'count' in df2.columns:
        df3 = df2.groupby('disjuncts')['count'].apply(sum).reset_index()  #OK
    elif 'counts' in df2.columns:
        df3 = df2.groupby('disjuncts')['counts'].apply(sum).reset_index()  #OK
    df4 = df2.groupby('disjuncts')['germs'].apply(sum).reset_index()  #OK
    if df4['disjuncts'].tolist() == df3['disjuncts'].tolist():
        if 'count' in df3.columns:
            df4['counts'] = df3['count']
        elif 'counts' in df3.columns:
            df4['counts'] = df3['counts']
    df4['disjuncts'] = df4['disjuncts'].apply(lambda x: list(x))
    return df4


def dedupe_entries(dfg):  # 80302 Turtle-5.1 used in 80303 5.2
    # dfg - grouped DataFrame 'germs':[], 'disjuncts':[], 'counts':int
    # Check each germ (word) belongs to only one rule (cluster, germ set)
    # If not: form a new single-germ-multi-disjunct entry ... then merge similar
    df = dfg.copy()
    words = set([y for x in df['germs'] for y in x])
    for word in words:
        ids = []
        for row in df.itertuples():
            if word in row[1]:
                ids.append(row[0])
        if len(ids) > 1:
            word_djs = []
            word_counts = 0
            print('dedupe_entries:', word, ids)
            for x in ids:  # TODO: check counts if applicable to 5.1
                word_count = int(df.loc[x]['counts']/len(df.loc[x]['germs']))
                df.loc[x]['counts'] -= word_count
                word_counts += word_count
                df.loc[x]['germs'].remove(word)
                word_djs.extend(df.loc[x]['disjuncts'])
            df.loc[len(df)] = [[word], word_djs, word_counts]
            print(df.loc[len(df)-1])
    return df


def lexical_entries(disjuncts):  # 80303 Turtle-5
    # build multi-germ-multi-disjunct lexical entries ~ LG rules (ALT 5.2 80303)
    df = disjuncts.copy()
    # merge_germ_disjuncts ~ build single-germ-multi-disjunct lexical entries
    df['disjuncts'] = [[x] for x in df['disjunct']]
    dfg = df.groupby('word').agg({'disjuncts': 'sum', 'count': 'sum'}).reset_index()
    # TODO: check multi-index in dfg, fix?
    dfg['germs'] = [[x] for x in dfg['word']]
    dfm = merge_disjunct_germs(dfg)[['germs', 'disjuncts','counts']]
    # TODO: loop dedupe-merge checking len(dfd) = len(dfg) ?
    dfd = dedupe_entries(dfg)  # overkill?
    dfm = merge_disjunct_germs(dfd)[['germs', 'disjuncts','counts']]
    return dfm


def entries2clusters(lexical_entries):  # 80303 Turtle-5 +80307
    df = lexical_entries.copy()
    df['germs'] = df['germs'].apply(lambda x: sorted(list(x)))
    df['disjuncts'] = df['disjuncts'].apply(lambda x: sorted(list(x)))
    df = df[['germs','disjuncts','counts']].sort_values(by='germs', ascending=True)
    df.index = ('C' + str(x).zfill(2) for x in range(1, len(df)+1))
    df['cluster'] = df.index  # added 80307 for disjuncts2clusters
    return df


def entries2rules(lexical_entries):  # 80303 Turtle-5
    rule_list = list()
    for row in lexical_entries.itertuples():
        rule = []
        rule.append(row[0])     # Cluster
        rule.append(row[1])     # Words
        rule.append([])         # Left Connectors
        rule.append([])         # Right Connectors
        rule.append(row[2])     # Disjuncts
        rule_list.append(rule)
    rule_list.sort()
    return rule_list


def disjuncts2clusters(lexical_entries):  # 80307 Turtle-5+ v.0.3
    df = lexical_entries.copy()
    wcs = dict()  # word-clusters
    for row in df.itertuples():
        for word in row[1]: wcs[word] = row[0]

    def connector(cluster, x, wcs):
        sign = str(x[-1])
        if sign == '-':
            return str(wcs[x[:-1]]) + cluster + '-'
        else:
            return cluster + str(wcs[x[:-1]]) + '+'
    def f(row):
        djs = row['disjuncts']
        cdjs = set()
        for x in djs:
            if '&' not in x:
                cdjs.add(connector(str(row['cluster']), x, wcs))
            else:
                z = []
                for y in x.split():
                    if (y != '&'):
                         z.append(connector(str(row['cluster']), y, wcs))
                cdjs.add(' & '.join(z))
        tmp = sorted(list(cdjs))
        return tmp

    df['disjuncts'] = df.apply(lambda row: f(row), axis=1)
    return df
