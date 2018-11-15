# language-learning/src/grammar_learner/pqa_table.py                    # 81109
# Test Grammar Learner to fill in ULL Project Plan Parses spreadshit
import os, sys, time
from ..common import handle_path_string
from ..grammar_tester import test_grammar
from ..grammar_tester.optconst import *
from .read_files import check_dir
from .learner import learn_grammar


def params(corpus, dataset, module_path, out_dir, **kwargs):            # 81114
    input_parses = module_path + '/data/' + corpus + '/' + dataset
    if type(kwargs['clustering']) is str:
        clustering = kwargs['clustering']
    else:
        clustering = kwargs['clustering'][0]
    if check_dir(input_parses, create=False, verbose='min'):
        batch_dir = out_dir + '/' + corpus
        spaces = ['w', 'c', 'd']        # 'words', 'connectors', 'disjuncts'
        context = spaces[kwargs['context']]
        rules = spaces[kwargs['grammar_rules']]
        if kwargs['grammar_rules'] == -1:
            rules = 'interconnected'
        elif kwargs['grammar_rules'] == -2:
            rules = 'linked'
        if kwargs['clustering'] == 'random':
            context = ''
            wtf = 'Random-clusters'

        else:
            wtf = abrvlg(**kwargs)  # 81114
        '''
        elif kwargs['word_space'] == 'vectors':\
            wtf = 'DRK'
        elif kwargs['word_space'] == 'discrete':
            wtf = 'ILE'
        elif kwargs['word_space'] == 'sparse':
            # wtf = 'ALE'  # 81109:
            if clustering == 'agglomerative':
                wtf = 'ALE'
            elif clustering in ['k-means', 'kmeans']:
                wtf = 'KLE'
            elif clustering[:4] == 'mean': # ['mean shift', 'mean_shift']:
                wtf = 'MLE'
            else:
                wtf = '?LE'
        else: wtf = '???'
        #'''

        if kwargs['left_wall'] in ['', 'none']:
            left_wall = 'no-LW'
        else: left_wall = 'LW'
        if kwargs['period']:
            period = 'RW'
        else: period = 'no-RW'
        generalization = ['no-gen', 'gen-cats', 'gen-rules', 'gen-both']
        gen = 0
        if 'categories_generalization' in kwargs:
            if kwargs['categories_generalization'] not in ['', 'off', 'none']:
                gen += 1
        if 'rules_generalization' in kwargs:
            if kwargs['rules_generalization'] not in ['', 'off', 'none']:
                gen += 2

        prj_dir = batch_dir + '_' + dataset + '_' + context + wtf + rules \
                  + '_' + left_wall + '_' + period + '_' + generalization[gen]

        if check_dir(prj_dir, create=True, verbose='none'):
            output_categories = prj_dir     # no file name ⇒ auto file name
            output_grammar = prj_dir        # no file name ⇒ auto file name
            return input_parses, output_categories, output_grammar
        else: return input_parses, out_dir, out_dir

    else:
        raise FileNotFoundError('File not found', input_parses)


def pqa_meter(dict_path, output_path, corpus_path, reference_path, **kwargs):
    grammar_path = output_path
    template_path = handle_path_string("tests/test-data/dict/poc-turtle")
    linkage_limit = kwargs['linkage_limit'] if 'linkage_limit' in kwargs else 1000
    if kwargs['linkage_limit'] == 0:
        return 0.0, 0.0, 0.0, 0.0   # table_rows: get grammar for further tests
    options = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY | BIT_ULL_IN  # | BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
    # 80719: BIT_ULL_IN :: use ull parses as test corpus
    # 80719: BIT_CAPS  :: preserve caps in parses, process inside Grammar Learner
    pa, f1, precision, recall = test_grammar(corpus_path, output_path, dict_path,
        grammar_path, template_path, linkage_limit, options, reference_path)
    pa = float(pa)
    recall = float(recall)

    return pa, f1, precision, recall


def table_rows(lines, out_dir, cp, rp, runs=(1, 1), **kwargs):          # 81021
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    if module_path not in sys.path: sys.path.append(module_path)
    header = ['Line', 'Corpus', 'Parsing', 'LW', 'RW', 'Gen.', 'Space',
              'Rules', 'Silhouette', 'PA', 'PQ', 'F1']
    spaces = ''
    if kwargs['clustering'] == 'random':
        spaces += 'RND'
    else:
        if kwargs['context'] == 1:
            spaces += 'c'
        else:
            spaces += 'd'
        if kwargs['word_space'] == 'vectors':
            spaces += 'DRK'
        elif kwargs['word_space'] == 'discrete':
            spaces += 'ILE'
        elif kwargs['word_space'] == 'sparse':
            if kwargs['clustering'][0] == 'agglomerative':
                spaces += 'ALE'
            elif kwargs['clustering'][0] in ['k-means', 'kmeans']:
                spaces += 'KLE'
            elif kwargs['clustering'][0][:4] == 'mean': # ['mean shift', 'mean_shift']:
                spaces += 'MLE'
            else:
                spaces += '?LE'
        else:
            spaces += '???'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    elif kwargs['grammar_rules'] == -1:  # 80825 interconnected connector-style
        spaces += 'ic'
    elif kwargs['grammar_rules'] == -2:  # 80825 interconnected disjunct-style
        spaces += 'id'
    else:
        spaces += 'd'
    details = []
    average = []
    for i, line in enumerate(lines):
        corpus = line[1]
        dataset = line[2]
        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' --- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' . '
        else:
            kwargs['period'] = False
            dot = ' --- '
        gen = line[5]  # none | rules | categories | both
        if gen in ['rules', 'both']:
            kwargs['rules_generalization'] = 'jaccard'
        else:
            kwargs['rules_generalization'] = 'off'
        if gen in ['categories', 'both']:
            kwargs['categories_generalization'] = 'jaccard'
        else:
            kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip, oc, og: input path, output categories, output grammar
        kwargs['input_parses'] = ip
        kwargs['output_grammar'] = og
        kwargs['output_categories'] = oc  # = output_grammar if absent or ''
        pa = []
        pq = []
        si = []  # Silhouiette index
        fm = []  # F-measure
        rules = []
        for j in range(runs[0]):
            try: # if True: #
                re = learn_grammar(**kwargs)
                if 'silhouette' in re:
                    s = round(re['silhouette'], 2)
                    s_str = str(s)
                else:
                    s = 0
                    s_str = ' --- '
            except: # else: #
                if kwargs['verbose'] not in ['none']:
                    print('pqa_table.py table_rows: learn_grammar(**kwargs)',
                          '⇒ exception:\n', sys.exc_info())
                pa.append(0.)
                pq.append(0.)
                rules.append(0)
                det_line = [line[0], corpus, dataset, lw, dot, gen, spaces,
                            ' fail ', ' --- ', ' --- ', ' --- ', ' --- ']
                details.append(det_line)
                continue
            if kwargs['linkage_limit'] > 0:  # use 0 to avoid grammar_tester call
                for i in range(runs[1]):
                    #-a,q,qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    a, f1, precision, q = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    fm.append(f1)
                    si.append(s)
                    rules.append(re['grammar_rules'])
                    dline = [line[0], corpus, dataset, lw, dot, gen, spaces,
                             ' ' + str(re['grammar_rules']) + ' ', s_str,
                             str(round(a*100))+'%', str(round(q*100))+'%',
                             str(round(f1, 2))]
                    details.append(dline)
            else:
                si.append(s)
                rules.append(re['grammar_rules'])
                print('else: details.append: re[grammar_rules]:', re['grammar_rules'],
                      're[silhouette]:', re['silhouette'], 's_str:', s_str)
                details.append([line[0], corpus, dataset, lw, dot, gen, spaces,
                                ' ' + str(re['grammar_rules']) + ' ', s_str,
                                ' --- ', ' --- ', ' --- '])
        if len(pa) > 0:
            pa_str = str(round(sum(pa) * 100 / len(pa))) + '%'
            pq_str = str(round(sum(pq) * 100 / len(pa))) + '%'
        else:
            pa_str = ' --- '
            pq_str = ' --- '
        if len(si) > 0:
            sia = round(sum(si) / len(si), 2)
        else: sia = 0.0
        sia_str = str(sia) if sia > 0.005 else ' --- '
        if len(fm) > 0:
            fm_str = str(round(sum(fm) / len(fm), 2))
        else: fm_str = ' --- '
        non_zero_rules = [x for x in rules if x > 0]
        if len(non_zero_rules) > 0:
            mean_rules = str(round(sum(non_zero_rules) / len(non_zero_rules)))
        else: mean_rules = 'fail'

        avg_line = [line[0], corpus, dataset, lw, dot, gen, spaces,
                    mean_rules, sia_str, pa_str, pq_str, fm_str]
        average.append(avg_line)

    return average, details, header


def abrvlg(**kwargs):
    if kwargs['word_space'] == 'vectors':
        return 'DRK'
    elif kwargs['word_space'] == 'discrete':
        return 'ILE'
    elif kwargs['word_space'] == 'sparse':
        if kwargs['clustering'][0] == 'agglomerative':
            x = kwargs['clustering']
            if len(x) < 2: x.append('ward')
            if len(x) < 3: x.append('euclidean')
            return 'AL' + x[1][0].upper() + x[2][0].upper()

        elif kwargs['clustering'][0] in ['k-means', 'kmeans']:
            return 'KLE'
        elif kwargs['clustering'][0][:4] == 'mean':  # ['mean shift', 'mean_shift']:
            return 'MLE'
        else:
            return '?LE'
    else:
        return '???'


def wide_rows(lines, out_dir, cp, rp, runs=(1, 1), **kwargs):          # 81114
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    if module_path not in sys.path: sys.path.append(module_path)
    #-header = ['Line', 'Corpus', 'Parsing', 'LW', 'RW', 'Gen.', 'Space',
    #-          'Rules', 'Silhouette', 'PA', 'PQ', 'F1']
    header = ['Line', 'Corpus', 'Parsing', 'Space', 'Linkage', 'Affinity',
              'Gen.', 'Rules', 'SI', 'PA', 'PQ', 'F1', 'Top 5 cluster sizes']

    spaces = ''
    if kwargs['clustering'] == 'random':
        spaces += 'RND'
    else:
        if kwargs['context'] == 1:
            spaces += 'c'
        else:
            spaces += 'd'
        spaces += abrvlg(**kwargs)

    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    elif kwargs['grammar_rules'] == -1:  # 80825 interconnected connector-style
        spaces += 'ic'
    elif kwargs['grammar_rules'] == -2:  # 80825 interconnected disjunct-style
        spaces += 'id'
    else:
        spaces += 'd'

    details = []
    average = []
    for i, line in enumerate(lines):
        corpus = line[1]
        dataset = line[2]
        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' --- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' . '
        else:
            kwargs['period'] = False
            dot = ' --- '
        gen = line[5]  # none | rules | categories | both
        if gen in ['rules', 'both']:
            kwargs['rules_generalization'] = 'jaccard'
        else:
            kwargs['rules_generalization'] = 'off'
        if gen in ['categories', 'both']:
            kwargs['categories_generalization'] = 'jaccard'
        else:
            kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip, oc, og: input path, output categories, output grammar
        kwargs['input_parses'] = ip
        kwargs['output_grammar'] = og
        kwargs['output_categories'] = oc  # = output_grammar if absent or ''
        pa = []
        pq = []
        si = []  # Silhouette index
        fm = []  # F-measure
        rules = []
        log = []
        cluster_sizes = []
        for j in range(runs[0]):
            try: # if True: #
                re = learn_grammar(**kwargs)
                cluster_sizes = [x for x in sorted(re['cluster_sizes'], reverse=True)[:5]]
                # cluster_sizes = [str(round(x*100/re['unique_words'])) + '%'
                #                 for x in sorted(re['cluster_sizes'], reverse=True)[:5]]
                log.append(re)
                if 'silhouette' in re:
                    s = round(re['silhouette'], 2)
                    s_str = str(s)
                else:
                    s = 0
                    s_str = ' --- '
            except: # else: #
                if kwargs['verbose'] not in ['none']:
                    print('pqa_table.py table_rows: learn_grammar(**kwargs)',
                          '⇒ exception:\n', sys.exc_info())
                pa.append(0.)
                pq.append(0.)
                rules.append(0)
                det_line = [line[0], corpus, dataset, spaces,
                            kwargs['clustering'][1], kwargs['clustering'][2], gen,
                            ' fail ', ' --- ', ' --- ', ' --- ', ' --- ', ' --- ']
                details.append(det_line)
                continue
            if kwargs['linkage_limit'] > 0:  # use 0 to avoid grammar_tester call
                for i in range(runs[1]):
                    #-a,q,qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    a, f1, precision, q = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    fm.append(f1)
                    si.append(s)
                    rules.append(re['grammar_rules'])
                    #-dline = [line[0], corpus, dataset, lw, dot, gen, spaces,
                    #         ' ' + str(re['grammar_rules']) + ' ', s_str,
                    #         str(round(a*100))+'%', str(round(q*100))+'%',
                    #         str(round(f1, 2))]
                    dline = [line[0], corpus, dataset, spaces,
                             kwargs['clustering'][1], kwargs['clustering'][2], gen,
                             ' ' + str(re['grammar_rules']) + ' ', s_str,
                             str(round(a*100))+'%', str(round(q*100))+'%',
                             str(round(f1, 2)), cluster_sizes]
                    details.append(dline)
            else:
                si.append(s)
                rules.append(re['grammar_rules'])
                print('else: details.append: re[grammar_rules]:', re['grammar_rules'],
                      're[silhouette]:', re['silhouette'], 's_str:', s_str)
                #-details.append([line[0], corpus, dataset, lw, dot, gen, spaces,
                #                ' ' + str(re['grammar_rules']) + ' ', s_str,
                #                ' --- ', ' --- ', ' --- '])
                details.append([line[0], corpus, dataset, spaces,
                                kwargs['clustering'][1], kwargs['clustering'][2], gen,
                                ' ' + str(re['grammar_rules']) + ' ', s_str,
                                ' --- ', ' --- ', ' --- ', ' --- '])
        if len(pa) > 0:
            pa_str = str(round(sum(pa) * 100 / len(pa))) + '%'
            pq_str = str(round(sum(pq) * 100 / len(pa))) + '%'
        else:
            pa_str = ' --- '
            pq_str = ' --- '
        if len(si) > 0:
            sia = round(sum(si) / len(si), 2)
        else: sia = 0.0
        sia_str = str(sia) if sia > 0.005 else ' --- '
        if len(fm) > 0:
            fm_str = str(round(sum(fm) / len(fm), 2))
        else: fm_str = ' --- '
        non_zero_rules = [x for x in rules if x > 0]
        if len(non_zero_rules) > 0:
            mean_rules = str(round(sum(non_zero_rules) / len(non_zero_rules)))
        else: mean_rules = 'fail'

        #-avg_line = [line[0], corpus, dataset, lw, dot, gen, spaces,
        #             mean_rules, sia_str, pa_str, pq_str, fm_str]
        avg_line = [line[0], corpus, dataset, spaces,
                    kwargs['clustering'][1], kwargs['clustering'][2], gen,
                    mean_rules, sia_str, pa_str, pq_str, fm_str, cluster_sizes]

        average.append(avg_line)

    return average, details, header, log


# Notes:

# 80802 /src/poc05.py restructured, def params moved here, further dev here
# legacy pqa_table.py renamed pqa05.py ~ poc05+pqa05=baseline (DEL later)
# 80825 kwargs['grammar_rules'] == -1,-2: interconnected clusters
# -1: connectors #Cxx: {C01Cxx- or ... CnCxx-} and {CxxC01+ or ... CxxCn+}
# -2: disjuncts  #Cxx: (C01Cxx-) or (C02Cxx-) ... or (CxxCn+)
# 81018: unified table_rows, ready for next test_grammar, table: PA/PQ/F1
# 81114: wider table for agglomerative clustering tests