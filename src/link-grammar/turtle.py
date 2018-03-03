import numpy as np
import pandas as pd


def single_disjuncts(word_links):  # 80223 Turtle-4
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


def link_grammar_rules(stalks):
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


def save_link_grammar(rule_list, path, file='', header='', footer=''):
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
    if file == '':
        out_file = path + 'turtle_link_grammar_' \
            + str(len(clusters)) + '_clusters_' + str(UTC())[:10] + '.4.0.dict'
    else: out_file = path + file
    if header == '':
        header = '% POC Turtle Link Grammar v.0.5 ' + str(UTC())
    if footer == '':
        footer = '% '+ str(len(clusters)) + ' word clusters, ' \
            + str(len(rule_list)) + ' Link Grammar rules.\n' \
            + '% Link Grammar file saved to: ' + out_file
    link_grammar = header +'\n\n'+ '\n'.join(line_list) +'\n\n'+ footer
    with open (out_file, 'w') as f: f.write(link_grammar)
    return link_grammar


def merge_clusters(threshold, n, clusters, sim_df):  # Turtle-4 80224 stub
    # 80224 Turtle 4 stub
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
