# language-learning/src/grammar_learner/write_files.py                  # 90119
import logging
import os, linkgrammar
from collections import OrderedDict
from copy import deepcopy
from .utl import UTC

def list2file(lst, out_file):
    string = ''
    for i, line in enumerate(lst):
        if i > 0: string += '\n'
        for j, x in enumerate(line):
            if isinstance(x, (list, set, tuple)):
                z = ' '.join(str(y) for y in x)
            else:
                try:
                    z = str(x)
                except TypeError:
                    z = 'ERROR'
            if j > 0: string += '\t'
            string += z
    with open(out_file, 'w') as f:
        f.write(string)
    return string


def rules2list(rules_dict, grammar_rules = 2, verbose = 'none'):
    logger = logging.getLogger(__name__ + ".rules2list")
    # rules_dict: {'cluster': [], 'words': [], } ⇒ return rules []
    # grammar_rules = kwargs['grammar_rules']: 1 - connectors, 2 - disjuncts

    sign = lambda x: ('+', '-')[x < 0]

    def disjunct(x, cluster_list, cluster):
        if x < 0:
            return cluster_list[abs(x)] + cluster + '-'
        else:
            return cluster + cluster_list[abs(x)] + '+'

    rules = []
    for i, cluster in enumerate(rules_dict['cluster']):
        if i == 0: continue
        if cluster is None: continue
        rule = [cluster]
        rule.append(sorted(rules_dict['words'][i]))
        if grammar_rules in [1,-1]:  # interconnected connector-based rules
            lefts = set()
            rights = set()
            for djtuple in rules_dict['disjuncts'][i]:
                for x in djtuple:
                    if x < 0:
                        lefts.add(disjunct(x, rules_dict['cluster'], cluster))
                    else:
                        rights.add(disjunct(x, rules_dict['cluster'], cluster))
            rule.append(sorted(lefts))
            rule.append(sorted(rights))
            rule.append('')
        else:  # rules: disjuncts
            rule.append('')  # lefts
            rule.append('')  # rights
            disjuncts = []
            for djtuple in rules_dict['disjuncts'][i]:
                try:
                    dj = ' & '.join(
                        [disjunct(x, rules_dict['cluster'], cluster)
                         for x in djtuple])
                    disjuncts.append(dj)
                except TypeError:
                    logger.critical(f'- wrong djtuple? - {djtuple}')
            rule.append(sorted(disjuncts))
        rules.append(rule)

    return rules


def save_link_grammar(rules, output_grammar, grammar_rules = 2,
                      header = '', footer = ''):  # legacy FIXME:DEL?
    # rules: [] or {}
    # grammar_rules = kwargs['grammar_rules']: 1 ⇒ connectors, 2+ ⇒ disjuncts
    if type(rules) is dict:
        rules = rules2list(rules, grammar_rules)

    line_list = list()
    clusters = set()
    for rule in rules:
        line = ''
        if len(rule[2]) > 0 and len(rule[3]) > 0:
            line += '{' + ' or '.join(
                str(x) for x in rule[2]) + '} & {' + ' or '.join(
                str(y) for y in rule[3]) + '}'
        else:
            if len(rule[2]) > 0:
                line += ' or '.join('(' + str(x) + ')' for x in rule[2])
            elif len(rule[3]) > 0:
                line += ' or '.join('(' + str(x) + ')' for x in rule[3])
        if len(rule[4]) > 0:
            if line != '': line += ' or '
            line += ' or '.join('(' + str(x) + ')' for x in rule[4])

        cluster_number = '% ' + str(rule[0]) + '\n'  # comment line: cluster
        cluster_and_words = ' '.join(
            '"' + word + '"' for word in rule[1]) + ':\n'
        line_list.append(cluster_number + cluster_and_words + line + ';\n')
        clusters.add(rule[0])

    line_list.sort()  # FIXME: overkill?

    if os.path.isfile(output_grammar):
        out_file = output_grammar
    elif os.path.isdir(output_grammar):
        out_file = output_grammar
        if out_file[-1] != '/': out_file += '/'
        out_file += 'dict_'
        out_file = out_file + str(len(clusters)) + 'C_' + str(UTC())[:10]
        if linkgrammar.__version__ == '5.4.4':  # 190128: restore LG 5.4.4 option
            out_file = out_file + '_0006.4.0.dict'
        else: out_file = out_file + '_0007.4.0.dict'
    else:
        raise FileNotFoundError('File not found', output_grammar)

    if header == '':
        header = '% Grammar Learner v.0.7 ' + str(UTC()) \
                 + '\n<dictionary-version-number>: V0v0v7+;\n'
        if linkgrammar.__version__ == '5.4.4':  # 190128: restore LG 5.4.4 option
            header = '% Grammar Learner v.0.6 ' + str(UTC()) \
            + '\n<dictionary-version-number>: V0v0v6+;\n'
    header = header + '<dictionary-locale>: EN4us+;'

    unknown_word = '<UNKNOWN-WORD>: XXX+;'
    if linkgrammar.__version__ == '5.4.4':  # 190128: restore LG 5.4.4 options
        unknown_word = 'UNKNOWN-WORD: XXX+;'

    if footer == '':
        footer = '% ' + str(len(clusters)) + ' word clusters, ' \
                 + str(len(rules)) + ' Link Grammar rules.\n'  # \
                # + '% Link Grammar file saved to: "' + out_file + '"'
                # 90110: Link Grammar sometimes parses (commented) filename 
    lg = header + '\n\n' + '\n'.join(line_list) + '\n' + unknown_word + '\n\n' + footer
    # lg = lg.replace('@', '.')  # 80706 WSD: word@1 ⇒ word.1  # removed  190804

    with open(out_file, 'w') as f: f.write(lg)

    response = OrderedDict([('grammar_file', out_file),
                            ('grammar_clusters', len(clusters)),
                            ('grammar_rules', len(rules))])
    return response


def save_category_tree(category_list, tree_file, verbose = 'none'):
    logger = logging.getLogger(__name__ + ".save_category_tree")
    cats = category_list
    clusters = {}
    m = 0
    for i, x in enumerate(cats):
        if x[0] not in clusters: clusters[x[0]] = []
        clusters[x[0]].append(i)
        if x[2] > m: m = x[2]
    tree = []
    for k, v in clusters.items():
        if len(v) == 1:
            tree.append(cats[v[0]])
        elif len(v) > 1:
            words = []
            similarities = []
            for j in v:
                words.extend(cats[j][4])
                similarities.extend(cats[j][5])
            tree.append(
                [cats[v[0]][0], 0, m + 1, cats[v[0]][3], words, similarities])
            for j in v:
                tree.append(
                    ['', m + 1, cats[j][2], cats[j][3], cats[j][4], cats[j][5]])
        else:
            logger.critical(f'WTF? {k} {v}')

    _ = list2file(tree, tree_file)

    return {'tree_file': tree_file}


def save_cat_tree(cats, output_categories, verbose = 'none'):
    # cats: {'cluster':[], 'words':[], ...}
    tree_file = output_categories
    if os.path.isdir(tree_file):  # received directory ⇒ auto file name
        if tree_file[-1] != '/': tree_file += '/'
        n_cats = len([x for i, x in enumerate(cats['cluster'])
                      if i > 0 and x is not None])
        tree_file += (str(n_cats) + '_cat_tree.txt')

    categories = []
    for i, cluster in enumerate(cats['cluster']):
        if i == 0:
            continue
        category = []
        if cats['cluster'][i] is not None:
            category.append(cats['cluster'][i])
        else:
            category.append('')
        category.append(cats['parent'][i])
        category.append(i)
        category.append(round(cats['quality'][i], 2))
        wordz = deepcopy(sorted(cats['words'][i]))
        #-wordz = [x.replace('@', '.') for x in wordz]  # WSD           # 190408
        category.append(wordz)  # 80704+06 tmp hack FIXME
        category.append(cats['similarities'][i])
        # -category.append(cats['children'][i])
        categories.append(category)

    _ = list2file(categories, tree_file)

    return {'cat_tree_file': tree_file}

# Notes:

# 80725 POC 0.1-0.4 deleted, 0.5 restructured, imports updated
# 80827 rules = -1/-2: interconnected clusters, connector/disjunct based rules
# 80929 save_link_grammar ⇒ 0.6
# 81003 save_link_grammar: Link Grammar ⇒ 5.5.1: UNKNOWN-WORD ⇒ <UNKNOWN-WORD>
# 81105 lines 121-123: ready to upgrade Link Grammar 5.4.4 ⇒ 5.5.1
# 81108 lines 116-125: check Link Grammar version and adapt grammar rules
# 81231 cleanup, version = 0.7 (LG 5.5.1), 0.6 (LG 5.4.4)
# 90110 remove filename
# 90119 remove Link Grammar 5.4.4 options (v.0.6)
# 90128 restore Link Grammar 5.4.4 'UNKNOWN-WORD: XXX+;' option
# 190428 WSD ⇒ learner: optional, configurable
