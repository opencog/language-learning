#!/usr/bin/env python3
#80510 POC 0.4: Proof of Concepf: Grammar Learner 0.4:

def list2file(lst, out_file):  # 80321 Turtle-8 - 80330 moved here from .utl.utl
    string = ''
    for i,line in enumerate(lst):
        if i > 0: string += '\n'
        for j,x in enumerate(line):
            if isinstance(x, (list, set, tuple)):
                z = ' '.join(str(y) for y in x)
            else:
                try: z = str(x)
                except TypeError: z = 'ERROR'
            if j > 0: string += '\t'
            string += z
    with open (out_file, 'w') as f: f.write(string)
    return string


#-def save_link_grammar(rules, path, file='', header='', footer=''):
def save_link_grammar(rules, output_grammar, header='', footer=''):  # 80510
    # rules - list
    import os
    from ..utl.utl import UTC
    #-if path[-1] != '/': path += '/'
    link_grammar = ''
    line_list = list()
    clusters = set()
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
    #TODO: file naming - corpus name?
    #-if file != '': out_file = path + file
    if os.path.isfile(output_grammar):
        out_file = output_grammar
    elif os.path.isdir(output_grammar):
        out_file = output_grammar
        if out_file[-1] != '/': out_file += '/'
        if 'isa' in '\t'.join(line_list):
            out_file += 'poc-turtle_'
        else: out_file += 'poc-english_'
        out_file = out_file + str(len(clusters)) + 'C_' \
            + str(UTC())[:10] + '_0004.4.0.dict'    #80511 0008 ⇒ 0004
    else: raise FileNotFoundError('File not found', output_grammar)
    if header == '':
        header = '% Grammar Learner v.0.4 ' + str(UTC())   #80511 .8 ⇒ .4
    header = header + '\n' + '<dictionary-version-number>: V0v0v4+;\n' \
        + '<dictionary-locale>: EN4us+;'
    add_rules = 'UNKNOWN-WORD: XXX+;'
    if footer == '':
        footer = '% '+ str(len(clusters)) + ' word clusters, ' \
            + str(len(rules)) + ' Link Grammar rules.\n' \
            + '% Link Grammar file saved to: ' + out_file
    lg = header +'\n\n'+ '\n'.join(line_list) +'\n'+ add_rules +'\n\n'+ footer
    with open (out_file, 'w') as f: f.write(lg)
    #-return lg  #80511 POC 0.4 replaced:
    from collections import OrderedDict
    response = OrderedDict({'grammar_file': out_file})
    response.update({'grammar_clusters': len(clusters), 'grammar_rules': len(rules)})
    return response


def save_category_tree(category_list, tree_file, verbose='none'):  #80522
    import os
    from src.utl.turtle import html_table
    from IPython.display import display
    cats = category_list
    clusters = {}
    m = 0
    for i,x in enumerate(cats):
        if x[0] not in clusters: clusters[x[0]] = []
        clusters[x[0]].append(i)
        if x[2] > m: m = x[2]
    tree = []
    for k,v in clusters.items():
        if len(v) == 1:
            tree.append(cats[v[0]])
        elif len(v) > 1:
            words = []
            similarities = []
            for j in v:
                words.extend(cats[j][4])
                similarities.extend(cats[j][5])
            tree.append([cats[v[0]][0], 0, m+1, cats[v[0]][3], words, similarities])
            for j in v:
                tree.append(['', m+1, cats[j][2], cats[j][3], cats[j][4], cats[j][5]])
        else: print('WTF?', k, v)
    if verbose in ['max', 'debug']:
        display(html_table([['Code','Parent','Id','Sim','Words','Similarities']] + tree))

    from src.utl.write_files import list2file
    #-tree_file = os.path.dirname(cat_file) + '/cat_tree.txt'
    string = list2file(tree, tree_file)

    return {'tree_file': tree_file}


#80331 list2file moved here from .utl.py
#80510 save_link_grammar moved here from src/link_grammar/poc.py & updated
#80522 save_category_tree
