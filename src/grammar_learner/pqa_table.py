# language-learning/src/grammar_learner/pqa_table.py                    # 190410
# Test Grammar Learner to fill in ULL Project Plan Parses spreadshit
import logging

# TODO: refactor 81217 wide_rows (archived) and ppln.py (make independent)

import os, sys, time
from ..common import handle_path_string
from ..grammar_tester import test_grammar
from ..common.optconst import *
from .utl import sec2string, kwa
from .read_files import check_dir
from .learner import learn_grammar, learn  # 81126 learn returns rules, log
from .write_files import list2file


def params(corpus_, dataset_, module_path_, out_dir, **kwargs):         # 90201
    corpus = kwargs['corpus'] if 'corpus' in kwargs else corpus_
    dataset = kwargs['dataset'] if 'dataset' in kwargs else dataset_
    module_path = kwargs['module_path'] if 'module_path' in kwargs else module_path_
    if 'input_parses' in kwargs:
        if module_path in kwargs['input_parses']:
            input_parses = kwargs['input_parses']
        else: input_parses = module_path + kwargs['input_parses']
    else: input_parses = module_path + '/data/' + corpus + '/' + dataset
    if type(kwargs['clustering']) is str:
        clustering = kwargs['clustering']
    else:
        clustering = kwargs['clustering'][0]
    if check_dir(input_parses, create=False, verbose='min'):
        batch_dir = out_dir + '/' + corpus
        spaces = ['w', 'c', 'd']  # 'words', 'connectors', 'disjuncts'
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
            wtf = abrvlg(**kwargs)

        if kwargs['left_wall'] in ['', 'none']:
            left_wall = 'no-LW'
        else:
            left_wall = 'LW'
        if kwargs['period']:
            period = 'RW'
        else:
            period = 'no-RW'

        generalization = ['no-gen', 'gen-cats', 'gen-rules', 'gen-both']
        gen = 0
        if 'categories_generalization' in kwargs:
            if kwargs['categories_generalization'] not in ['', 'off', 'none']:
                gen += 1
        if 'rules_generalization' in kwargs:
            if kwargs['rules_generalization'] not in ['', 'off', 'none']:
                gen += 2

        prj_dir = batch_dir + '_' + dataset + '_' + context + wtf + rules \
                  + '_' + generalization[gen]
        if 'cluster_range' in kwargs:
            if type(kwargs['cluster_range']) is int:
                prj_dir = prj_dir + '_' + str(kwargs['cluster_range']) + 'c'

        if 'min_word_count' in kwargs and kwargs['min_word_count'] > 1:
            prj_dir = prj_dir + '_mwc=' + str(kwargs['min_word_count'])

        if len(kwargs['clustering']) > 3 \
                and type(kwargs['clustering'][3]) is int:
            prj_dir = prj_dir + '_' + str(['clustering'][3]) + 'nn'
            # number of nearest neighbors in connectivity constraints   # 81116

        if check_dir(prj_dir, create=True, verbose='none'):
            output_categories = prj_dir  # no file name ⇒ auto file name
            output_grammar = prj_dir     # no file name ⇒ auto file name
            return input_parses, output_categories, output_grammar
        else:
            return input_parses, out_dir, out_dir

    else:
        raise FileNotFoundError('File not found', input_parses)


def pqa_meter(dict_path, op, cp, rp, **kwargs):   # TODO: restore previous
    # op,cp,rp: ex. output_path, corpus_path, reference_path - changed 90131:
    corpus_path = cp if len(cp) > 0 else kwargs['corpus_path']
    reference_path = rp if len(rp) > 0 else kwargs['reference_path']
    if len(op) > 0:
        output_path = op
        grammar_path = op
    else:
        grammar_path = kwargs['output_grammar']
        output_path = kwargs['out_path'] if 'out_path' in kwargs \
            else kwargs['output_grammar']

    template_path = handle_path_string("tests/test-data/dict/poc-turtle") # FIXME:WTF?
    linkage_limit = kwargs['linkage_limit'] if 'linkage_limit' in kwargs else 1000
    if 'linkage_limit' == 0:
        return 0.0, 0.0, 0.0, 0.0  # table_rows: get grammar for further tests
    options = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY | BIT_ULL_IN  # | BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
    # BIT_ULL_IN :: use ull parses as test corpus
    # BIT_CAPS  :: preserve caps in parses, process inside Grammar Learner

    pa, f1, precision, recall = \
        test_grammar(corpus_path, output_path, dict_path, grammar_path,
                     template_path, linkage_limit, options, reference_path)

    return float(pa), float(f1), float(precision), float(recall)


def table_rows(lines, out_dir, cp, rp, runs=(1, 1), **kwargs):
    # cp: corpus_path, rp: reference_path for grammar tester
    logger = logging.getLogger(__name__ + ".table_rows")
    module_path = os.path.abspath(os.path.join('..'))
    if module_path not in sys.path: sys.path.append(module_path)
    header = ['Line', 'Corpus', 'Parsing', 'LW', 'RW', 'Gen.', 'Space', 'Rules',
              'Silhouette', 'PA', 'PQ', 'F1']
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
            elif kwargs['clustering'][0][:4] == 'mean':  # ['mean shift', ...]
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
        if kwargs['grammar_rules'] == 1 and gen != 'none':
            continue

        corpus = line[1]
        dataset = line[2]
        if 'input_parses' in kwargs:
            del kwargs['input_parses']
        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip, oc, og: input path, output categories, output grammar
        kwargs['input_parses'] = ip
        kwargs['output_grammar'] = og
        kwargs['output_categories'] = oc  # = output_grammar if absent or ''
        pa = []  # «parse-ability»
        pq = []  # «parse quality» ~ recall
        si = []  # Silhouette index
        fm = []  # F-measure (F1)
        rules = []
        for j in range(runs[0]):
            try:  # if True: #
                re = learn_grammar(**kwargs)
                if 'silhouette' in re:
                    s = round(re['silhouette'], 2)
                    s_str = str(s)
                else:
                    s = 0
                    s_str = ' --- '
            except:  # else: #
                logger.critical('pqa_table.py table_rows:',
                                'learn_grammar(**kwargs) ⇒ exception:\n',
                                sys.exc_info())
                pa.append(0.)
                pq.append(0.)
                rules.append(0)
                det_line = [line[0], corpus, dataset, lw, dot, gen, spaces,
                            ' fail ', ' --- ', ' --- ', ' --- ', ' --- ']
                details.append(det_line)
                continue
            if kwargs['linkage_limit'] > 0:
                for k in range(runs[1]):
                    a, f1, precision, q = pqa_meter(re['grammar_file'],
                                                    og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    fm.append(f1)
                    si.append(s)
                    rules.append(re['grammar_rules'])
                    dline = [line[0], corpus, dataset, lw, dot, gen, spaces,
                             ' ' + str(re['grammar_rules']) + ' ', s_str,
                             str(round(a * 100)) + '%',
                             str(round(q * 100)) + '%', str(round(f1, 2))]
                    details.append(dline)
            else:
                si.append(s)
                rules.append(re['grammar_rules'])
                details.append([line[0], corpus, dataset, lw, dot, gen, spaces,
                                ' ' + str(re['grammar_rules']) + ' ',
                                s_str, ' --- ', ' --- ', ' --- '])
        if len(pa) > 0:
            pa_str = str(round(sum(pa) * 100 / len(pa))) + '%'
            pq_str = str(round(sum(pq) * 100 / len(pa))) + '%'
        else:
            pa_str = ' --- '
            pq_str = ' --- '
        if len(si) > 0:
            sia = round(sum(si) / len(si), 2)
        else:
            sia = 0.0
        sia_str = str(sia) if sia > 0.005 else ' --- '
        if len(fm) > 0:
            fm_str = str(round(sum(fm) / len(fm), 2))
        else:
            fm_str = ' --- '
        non_zero_rules = [x for x in rules if x > 0]
        if len(non_zero_rules) > 0:
            mean_rules = str(round(sum(non_zero_rules) / len(non_zero_rules)))
        else:
            mean_rules = 'fail'

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
            x = list(kwargs['clustering'])
            if len(x) < 2: x.append('ward')
            if len(x) < 3: x.append('euclidean')
            return 'AL' + x[1][0].upper() + x[2][0].upper()
        elif kwargs['clustering'][0] in ['k-means', 'kmeans']:
            return 'KLE'
        elif kwargs['clustering'][0][:4] == 'mean':  # mean shift
            return 'MLE'
        else:
            return '?LE'
    else:
        return '???'


def wide_rows(lines, out_dir, cp, rp, runs=(1, 1), **kwargs):
    # cp: (test) corpus_path, rp: reference_path for grammar tester
    start = time.time()
    logger = logging.getLogger(__name__ + ".wide_rows")
    module_path = os.path.abspath(os.path.join('..'))
    if module_path not in sys.path: sys.path.append(module_path)
    header = ['Line', 'Corpus', 'Parsing', 'Space', 'Linkage', 'Affinity',
              'G12n', 'Threshold', 'Rules', 'MWC', 'NN', 'SI',
              'PA', 'PQ', 'F1']
    if '+' in kwargs['verbose']:
        header.append('Top 5 cluster sizes')

    linkage = '---'
    affinity = '---'
    rgt = '---'  # rules_generalization_threshold
    knn = '---'  # k nearest neighbors for connectivity graph

    clustering = kwa(['agglomerative', 'ward', 'euclidean'], 'clustering', **kwargs)
    if type(clustering) is str:
        if clustering == 'kmeans':
            clustering = ['kmeans', 'k-means++', 10]
        elif clustering == 'agglomerative':
            clustering = ['agglomerative', 'ward', 'euclidean']
        elif clustering == 'mean_shift':
            clustering = ['mean_shift', 'auto']
        elif clustering == 'group':  # TODO: call ILE clustering?
            print('Call ILE clustering from optimal_clusters?')
        elif clustering == 'random':  # TODO: call random clustering?
            print('Call random clustering from optimal_clusters?')
        else:
            clustering = ['agglomerative', 'ward', 'euclidean']

    if len(clustering) > 3:
        if type(kwargs['clustering'][3]) is int:
            knn = kwargs['clustering'][3]
    if clustering[0] == 'agglomerative':
        linkage = clustering[1]
        if len(clustering) > 2:
            affinity = clustering[2]
        else:
            affinity = 'euclidean'
    else:
        linkage = clustering[0]             # FIXME: all options...

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
    elif kwargs['grammar_rules'] == -1:  # interconnected connector-style
        spaces += 'ic'
    elif kwargs['grammar_rules'] == -2:  # interconnected disjunct-style
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
        else:
            kwargs['left_wall'] = ''
        if line[4] != 0:
            kwargs['period'] = True
        else:
            kwargs['period'] = False

        gen = line[5]  # none | rules | categories | both | old | updated | new
        if 'rules_aggregation' in kwargs \
                and type(kwargs['rules_aggregation']) is float:
            rgt = str(kwargs['rules_aggregation'])  # rules g12n threshold
            if gen in ['rules', 'both', 'old', 'jaccard']:
                kwargs['rules_generalization'] = 'jaccard'
            elif gen in ['updated', 'hierarchical', 'hier.', 'HDJ']:
                kwargs['rules_generalization'] = 'hierarchical'
                gen = 'HDJ'  # Hierarchical: Disjuncts Jaccard index similarity
            elif gen in ['new', 'fast']:
                kwargs['rules_generalization'] = 'fast'
                gen = 'fast'
            else:
                kwargs['rules_generalization'] = 'off'
                rgt = '---'  # rules_generalization_threshold
        if gen in ['categories', 'both']:
            kwargs['categories_generalization'] = 'jaccard'
        else:
            kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none':
            continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip, oc, og: input path, output categories, output grammar
        kwargs['input_parses'] = ip
        kwargs['output_grammar'] = og
        kwargs['output_categories'] = oc  # = output_grammar if absent or ''

        # Averaging ::  FIXME: stop averaging?
        pa = []  # «parse-ability»
        pq = []  # «parse quality»
        si = []  # Silhouette index
        fm = []  # F-measure (F1)
        rules = []
        cluster_sizes = []
        for j in range(runs[0]):
            try:  # if True:  #
                rulez, re = learn(**kwargs)

                if len(rulez) < 1:  # empty filtered dataset            # 190410
                    msg = [['Error:', 'empty', 'filtered', 'parses', 'dataset', '⇒',
                            'check', 'max_unparsed_words', 'in', 'kwargs']]
                    return msg, msg, header, re, rulez

                if 'rule_sizes' in re:
                    cluster_sizes = sorted(re['rule_sizes'].keys(),
                                           reverse=True)[:5]
                elif 'cluster_sizes' in re:
                    cluster_sizes = sorted(re['cluster_sizes'].keys(),
                                           reverse=True)[:5]
                if 'silhouette' in re:
                    s = round(re['silhouette'], 2)
                    s_str = str(s)
                else:
                    s = 0
                    s_str = ' --- '
            except:  # else: #
                logger.critical('pqa_table.py wide_rows:',
                                'learn_grammar(**kwargs) ⇒ exception:\n',
                                sys.exc_info())
                pa.append(0.)
                pq.append(0.)
                rules.append(0)
                det_line = [line[0], corpus, dataset, spaces,
                            linkage, affinity, gen, ' ---', 'fail',
                            ' ---', ' ---', ' ---', ' ---', ' ---', ' ---']
                details.append(det_line)
                continue  # FIXME: check case
            if kwargs['linkage_limit'] > 0:
                start = time.time()
                for k in range(runs[1]):
                    a, f1, precision, q = pqa_meter(re['grammar_file'],
                                                    og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    fm.append(f1)
                    si.append(s)
                    rules.append(re['grammar_rules'])
                    dline = [line[0], corpus, dataset, spaces,
                             linkage, affinity, gen, rgt,
                             ' ' + str(re['grammar_rules']) + ' ',
                             str(kwargs['min_word_count']), s_str,
                             str(knn), str(round(a * 100)) + '%',
                             str(round(q * 100)) + '%', str(round(f1, 2))]
                    if '+' in kwargs['verbose']:
                        dline.append(cluster_sizes)
                    details.append(dline)
            else:  # kwargs['linkage_limit'] = 0 :: avoid grammar_tester call
                si.append(s)
                rules.append(re['grammar_rules'])
                details.append([line[0], corpus, dataset, spaces,
                                linkage, affinity, gen, rgt,
                                ' ' + str(re['grammar_rules']) + ' ',
                                str(kwargs['min_word_count']), s_str,
                                str(knn), '---', ' ---', ' ---', ' ---'])
        if len(pa) > 0:
            pa_str = str(round(sum(pa) * 100 / len(pa))) + '%'
            pq_str = str(round(sum(pq) * 100 / len(pa))) + '%'
        else:
            pa_str = ' --- '
            pq_str = ' --- '
        if len(si) > 0:
            sia = round(sum(si) / len(si), 2)
        else:
            sia = 0.0
        sia_str = str(sia)  # if sia > 0.005 else ' --- '
        if len(fm) > 0:
            fm_str = str(round(sum(fm) / len(fm), 2))
        else:
            fm_str = ' --- '
        non_zero_rules = [x for x in rules if x > 0]
        if len(non_zero_rules) > 0:
            mean_rules = str(round(sum(non_zero_rules) / len(non_zero_rules)))
        else:
            mean_rules = 'fail'

        avg_line = [line[0], corpus, dataset, spaces, linkage, affinity,
                    gen, rgt, mean_rules, str(kwargs['min_word_count']),
                    str(knn), sia_str, pa_str, pq_str, fm_str, cluster_sizes]

        average.append(avg_line)

    re.update({'grammar_test_time': sec2string(time.time() - start)})

    stats = []
    if 'cleaned_words' in re:
        stats.append(['Clean corpus size ', re['cleaned_words']])
    if 'grammar_learn_time' in re:
        stats.append(['Grammar learn time', re['grammar_learn_time']])
    if 'grammar_test_time' in re:
        stats.append(['Grammar test time ', re['grammar_test_time']])
    if len(stats) > 0:
        x = re['corpus_stats_file']
        list2file(stats, x[:x.rfind('/')] + '/learn_&_test_stats.txt')
    # return average, details, header, re
    return average, details, header, re, rulez  # 81120 tmp FIXME:DEL rulez?


def wide_table(lines, out_dir, cp, rp, **kwargs):           # 81222 FIXME: [»]
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    # runs = (1,1) (...rows) unused ⇒ FIXME:DEL from calls! [»]
    # ? module_path = os.path.abspath(os.path.join('..'))
    # ? if module_path not in sys.path: sys.path.append(module_path)
    header = ['Line', 'Corpus', 'Parsing', 'Space', 'Linkage', 'Affinity',
              'G12n', 'Threshold', 'Rules', 'MWC', 'NN', 'SI',
              'PA', 'PQ', 'F1']
    if 'log+' in kwargs['verbose']:
        header.append('Top 5 cluster sizes')

    linkage = '---'
    affinity = '---'
    rgt = '---'  # rules_generalization_threshold
    knn = '---'  # k nearest neighbors for connectivity graph

    clustering = kwa(['agglomerative', 'ward', 'euclidean'], 'clustering',
                     **kwargs)
    if type(clustering) is str:
        if clustering == 'kmeans':
            clustering = ['kmeans', 'k-means++', 10]
        elif clustering == 'agglomerative':
            clustering = ['agglomerative', 'ward', 'euclidean']
        elif clustering == 'mean_shift':
            clustering = ['mean_shift', 'auto']
        elif clustering == 'group':  # TODO: call ILE clustering?
            print('Call ILE clustering from optimal_clusters?')
        elif clustering == 'random':  # TODO: call random clustering?
            print('Call random clustering from optimal_clusters?')
        else:
            clustering = ['agglomerative', 'ward', 'euclidean']

    if len(clustering) > 3:
        if type(kwargs['clustering'][3]) is int:
            knn = kwargs['clustering'][3]
    if clustering[0] == 'agglomerative':
        linkage = clustering[1]
        if len(clustering) > 2:
            affinity = clustering[2]
        else: affinity = 'euclidean'
    else:
        linkage = clustering[0]             # FIXME: all options...

    spaces = ''
    if kwargs['clustering'] == 'random':
        spaces += 'RND'
    else:
        if kwargs['context'] == 1:
            spaces += 'c'
        else: spaces += 'd'
        spaces += abrvlg(**kwargs)

    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    elif kwargs['grammar_rules'] == -1:  # interconnected connector-style
        spaces += 'ic'
    elif kwargs['grammar_rules'] == -2:  # interconnected disjunct-style
        spaces += 'id'
    else: spaces += 'd'

    details = []
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

        gen = line[5]  # none | rules | categories | both | old | updated | new
        if 'rules_aggregation' in kwargs \
                and type(kwargs['rules_aggregation']) is float:
            rgt = str(kwargs['rules_aggregation'])
            if gen in ['rules', 'both', 'old', 'jaccard']:
                kwargs['rules_generalization'] = 'jaccard'
            elif gen in ['updated', 'hierarchical', 'hier.', 'HDJ']:
                kwargs['rules_generalization'] = 'hierarchical'
                gen = 'HDJ'
            elif gen in ['new', 'fast']:
                kwargs['rules_generalization'] = 'fast'
                gen = 'fast'
            else:
                kwargs['rules_generalization'] = 'off'
                rgt = '---'  # rules_generalization_threshold
        if gen in ['categories', 'both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip, oc, og: input path, output categories, output grammar
        kwargs['input_parses'] = ip
        kwargs['output_grammar'] = og
        kwargs['output_categories'] = oc  # = output_grammar if absent or ''

        if True:  # try:  #
            rulez, re = learn(**kwargs)
            if 'rule_sizes' in re:
                cluster_sizes = sorted(re['rule_sizes'].keys(), reverse=True)[:5]
            elif 'cluster_sizes' in re:
                cluster_sizes = sorted(re['cluster_sizes'].keys(), reverse=True)[:5]
            if 'silhouette' in re:
                s = round(re['silhouette'], 2)
                s_str = str(s)
            else:
                s = 0
                s_str = ' --- '
        else:  # except:  #
            logger.critical('pqa_table.py wide_table:',
                            'learn_grammar(**kwargs) ⇒ exception:\n',
                            sys.exc_info())
            dline = [line[0], corpus, dataset, spaces,
                     linkage, affinity, gen, ' ---', 'fail',
                     ' ---', ' ---', ' ---', ' ---', ' ---', ' ---']
            details.append(dline)
            continue  # FIXME: check case
        if kwargs['linkage_limit'] > 0:
            start = time.time()
            a, f1, precision, q = pqa_meter(re['grammar_file'],
                                            og, cp, rp, **kwargs)
            dline = [line[0], corpus, dataset, spaces,
                     linkage, affinity, gen, rgt,
                     ' ' + str(re['grammar_rules']) + ' ',
                     str(kwargs['min_word_count']),
                     s_str, str(knn), str(round(a * 100)) + '%',
                     str(round(q * 100)) + '%', str(round(f1, 2))]
            if 'log+' in kwargs['verbose']:
                dline.append(cluster_sizes)
        else:
            rules.append(re['grammar_rules'])
            dline = [line[0], corpus, dataset, spaces,
                     linkage, affinity, gen, rgt,
                     ' ' + str(re['grammar_rules']) + ' ',
                     str(kwargs['min_word_count']),
                     s_str, str(knn), ' ---', ' ---', ' ---']
        details.append(dline)

    re.update({'grammar_test_time': sec2string(time.time() - start)})
    stats = []
    if 'grammar_learn_time' in re:
        stats.append(['Grammar learn time', re['grammar_learn_time']])
    if 'grammar_test_time' in re:
        stats.append(['Grammar test time ', re['grammar_test_time']])
    if len(stats) > 0:
        x = re['corpus_stats_file']
        list2file(stats, x[:x.rfind('/')] + '/learn_&_test_stats.txt')

    return header, details, re


# Notes:

# 80802 /src/poc05.py restructured, def params moved here, further dev here
# legacy pqa_table.py renamed pqa05.py ~ poc05+pqa05=baseline (DEL later)
# 80825 kwargs['grammar_rules'] == -1,-2: interconnected clusters
# -1: connectors #Cxx: {C01Cxx- or ... CnCxx-} and {CxxC01+ or ... CxxCn+}
# -2: disjuncts  #Cxx: (C01Cxx-) or (C02Cxx-) ... or (CxxCn+)
# 81018 unified table_rows, ready for next test_grammar, table: PA/PQ/F1
# 81114 wider table for agglomerative clustering tests
# 81120 wide_rows
# 81210 wide_rows + min_word_count
# 81220 wide_table ⇒ FIXME in 2019, replace wide_row in 2019 .ipynb tests.
# 81231 cleanup
# 190221 tweak min_word_count (line 69)
# 190410 fix empty filtered dataset issue
