#language-learning/src/grammar_learner/write_files.py                   80827
import os
from collections import OrderedDict
from copy import deepcopy
from .utl import UTC
from .widgets import html_table, display

def list2file(lst, out_file):  # 80321
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


def rules2list(rules_dict, grammar_rules=2, verbose='none'):   #80620 0.5 {} ⇒ [] ⇒ save_link_grammar
    # rules_dict: {'cluster': [], 'words': [], }
    # grammar_rules = kwargs['grammar_rules']: 1 - connectors, 2 - disjuncts

    sign = lambda x: ('+','-')[x < 0]
    def disjunct(x, cluster_list, cluster):
        if x < 0:
            return cluster_list[abs(x)] + cluster + '-'
        else: return cluster + cluster_list[abs(x)] + '+'
    rules = []
    for i,cluster in enumerate(rules_dict['cluster']):
        if i == 0: continue
        if cluster == None: continue
        if verbose == 'debug':
            print('rules2list:', i, cluster, rules_dict['disjuncts'][i])
        rule = [cluster]
        rule.append(sorted(rules_dict['words'][i]))
        #if grammar_rules == 1:      # rules based on connectors  #80827:
        if grammar_rules in [1,-1]:  # rules based on connectors, interconnected
            lefts = set()
            rights = set()
            for djtuple in rules_dict['disjuncts'][i]:
                for x in djtuple:
                    if x < 0:
                        lefts.add(disjunct(x, rules_dict['cluster'], cluster))
                    else: rights.add(disjunct(x, rules_dict['cluster'], cluster))
            rule.append(sorted(lefts))
            rule.append(sorted(rights))
            rule.append('')   #disjuncts
            if verbose == 'debug':
                print('connector-based rule:', i, cluster, rule)
        else:   # rules: disjuncts  #TODO: 2/3/4...
            rule.append('')   #lefts
            rule.append('')   #rights
            disjuncts = []
            for djtuple in rules_dict['disjuncts'][i]:
                try:
                    dj = ' & '.join([disjunct(x, rules_dict['cluster'], cluster) \
                        for x in djtuple])
                    disjuncts.append(dj)
                except TypeError:
                    print('- wrong djtuple? -', djtuple)
            rule.append(sorted(disjuncts))
            if verbose == 'debug':
                print('disjunct-based rule  :', i, cluster, rule)
        rules.append(rule)
    return rules


def save_link_grammar(rules, output_grammar,
                      grammar_rules=2, header='', footer=''):       #   80929
    # rules: [] or {} -
    # grammar_rules = kwargs['grammar_rules']: 1 ⇒ connectors, 2+ ⇒ disjuncts

    if type(rules) is dict:
        rules = rules2list(rules, grammar_rules)

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

    if os.path.isfile(output_grammar):
        out_file = output_grammar
    elif os.path.isdir(output_grammar):
        out_file = output_grammar
        if out_file[-1] != '/': out_file += '/'
        out_file += 'dict_'
        out_file = out_file + str(len(clusters)) + 'C_' \
            + str(UTC())[:10] + '_0006.4.0.dict'            # 80929 0005⇒0006
    else: raise FileNotFoundError('File not found', output_grammar)
    if header == '':
        header = '% Grammar Learner v.0.6 ' + str(UTC())    # 80929 .5⇒.6
    header = header + '\n' + '<dictionary-version-number>: V0v0v5+;\n' \
        + '<dictionary-locale>: EN4us+;'
    add_rules = 'UNKNOWN-WORD: XXX+;'
    if footer == '':
        footer = '% '+ str(len(clusters)) + ' word clusters, ' \
            + str(len(rules)) + ' Link Grammar rules.\n' \
            + '% Link Grammar file saved to: ' + out_file
    lg = header +'\n\n'+ '\n'.join(line_list) +'\n'+ add_rules +'\n\n'+ footer
    lg = lg.replace('@', '.')       #80706 WSD: word@1 ⇒ word.1  FIXME:DEL?
    with open (out_file, 'w') as f: f.write(lg)

    response = OrderedDict({'grammar_file': out_file})
    response.update({'grammar_clusters': len(clusters), 'grammar_rules': len(rules)})
    return response


def save_category_tree(category_list, tree_file, verbose='none'):
    #+from write_files import list2file
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

    #-tree_file = os.path.dirname(cat_file) + '/cat_tree.txt'
    string = list2file(tree, tree_file)

    return {'tree_file': tree_file}


def save_cat_tree(cats, output_categories, verbose='none'):
    # cats: {'cluster':[], 'words':[], ...}
    #+from write_files import list2file

    tree_file = output_categories
    if '.' not in tree_file:  #auto file name
        if tree_file[-1] != '/': tree_file += '/'
        n_cats = len([x for i,x in enumerate(cats['parent']) if i > 0 and x < 1])
        tree_file += (str(n_cats) + '_cat_tree.txt')

    categories = []
    for i,cluster in enumerate(cats['cluster']):
        if i == 0: continue
        category = []
        if cats['cluster'][i] is not None:
            category.append(cats['cluster'][i])
        else: category.append('')
        category.append(cats['parent'][i])
        category.append(i)
        category.append(round(cats['quality'][i],2))
        wordz = deepcopy(sorted(cats['words'][i]))
        wordz = [x.replace('@','.') for x in wordz] #80706 WSD: word@1 ⇒ word.1
        category.append(wordz)                      #80704+06 tmp hack FIXME
        category.append(cats['similarities'][i])
        #-category.append(cats['children'][i])
        categories.append(category)

    string = list2file(categories, tree_file)

    if verbose in ['max', 'debug']:
        print(UTC(),':: src/utl.writefiles.py save_cat_tree:', \
            len(cats['cluster']) - 1, 'categories')
    if verbose == 'debug':
        display(html_table([['Code','Parent','Id','Sim','Words','Similarities']] + categories))

    return {'cat_tree_file': tree_file}


#Notes:

#80331 list2file moved here from .utl.py
#80510 save_link_grammar moved here from src/link_grammar/poc.py & updated
#80522 save_category_tree
#80619 save_cat_tree, +80623 auto file name
#80620 0.5 new data structure, rules2list, 80626 connector-based rules
#80706 WSD: word@1 ⇒ word.1
#80725 POC 0.1-0.4 deleted, 0.5 restructured, imports updated
#80827 rules = -1/-2: interconnected clusters, connector/disjunct based rules
#80929 save_link_grammar ⇒ 0.6
