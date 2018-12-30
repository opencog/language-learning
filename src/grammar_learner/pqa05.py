#Legacy Grammar Learner testL fill in ULL Project Plan Parses spreadshit
#language-learning/src/grammar_learner/pqa_table.py 80725, renamed pqa05 #80802
import logging
import os
import sys
import time
from ..common.cliutils import handle_path_string
from ..grammar_tester.grammartester import test_grammar
from ..grammar_tester.optconst import * # import * only allowed at module level
from .poc05 import learn_grammar, params

def pqa_meter(input_path, output_grammar, corpus_path, reference_path, runs=(1,1), **kwargs):
    #80720 test_grammar_wrapped 2.0
    output_path   = output_grammar
    dict_path     = input_path
    grammar_path  = output_grammar
    template_path = handle_path_string("tests/test-data/dict/poc-turtle")
    linkage_limit = kwargs['linkage_limit'] #100
    options = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY | BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
    #80719 added BIT_ULL_IN for table_cds - Child Directed Speech
    #80719: BIT_CAPS = preserve caps
    pa, pq, pqa = test_grammar(corpus_path, output_path, dict_path, \
        grammar_path, template_path, linkage_limit, options, reference_path)
    return pa, pq, pqa


def table_damb(lines, out_dir, cps=(0,0), rps=(0,0), runs=(1,1), **kwargs):  #-lines, module_path,
    #80720: table_amb 2.0: module_path, corpus_path, test_path built-in
    # cps,rps: tuples len=2 corpus_paths, reference_paths for Amb and disAmb corpora
    module_path = os.path.abspath(os.path.join('..'))
    # if module_path not in sys.path: sys.path.append(module_path)
    rpd = module_path + '/data/POC-English-Amb/MST-fixed-manually/poc-english_ex-parses-gold.txt'

    spaces = ''
    if kwargs['context'] == 1:
        spaces += 'c'
    else: spaces += 'd'
    if kwargs['word_space'] == 'vectors':
        spaces += 'DRK'
    else: spaces += 'ILE'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    else: spaces += 'd'

    details = []
    average = []

    for i,line in enumerate(lines):
        corpus = line[1]
        if corpus == 'POC-English-disAmb':
            if cps[1] == 0:
                cp = rpd  # default reference_path
            else: cp = cps[1]
            if rps[1] == 0:
                rp = rpd
            else: rp = rps[1]
        else:
            if cps[0] == 0:
                cp = rpd
            else: cp = cps[0]
            if rps[0] == 0:
                rp = rpd
            else: rp = rps[0]

        dataset = line[2]

        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' -- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' + '
        else:
            kwargs['period'] = False
            dot = ' -- '

        gen = line[5]  # none | rules | categories | both
        if gen in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if gen in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen not in ['none','off']: continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        # ip,oc,og :: input_path, output_categories, output_grammar
        pa = []
        pq = []
        rules = []
        for j in range(runs[0]):
            re = learn_grammar(ip, oc, og, **kwargs)
            for i in range(runs[1]):
                a, q, qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                pa.append(a)
                pq.append(q)
                rules.append(re['grammar_rules'])
                rulestr = ' ' + str(re['grammar_rules']) + ' '
                line = [line[0], corpus, dataset, lw, dot, gen, spaces, rulestr, \
                        str(int(round(a,0)))+'%', str(int(round(q,0)))+'%']
                details.append(line)
        paa = int(round(sum(pa)/len(pa), 0))
        pqa = int(round(sum(pq)/len(pq), 0))
        rules_avg = int(round(sum(rules)/len(rules), 0))
        avg = [line[0], corpus, dataset, lw, dot, gen, spaces, rules_avg, \
               str(paa)+'%', str(pqa)+'%']
        average.append(avg)
    return average, details


def table_cds(lines, out_dir, cp, rp, runs=(1,1), **kwargs):
    logger = logging.getLogger(__name__ + ".table_cds")
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    # if module_path not in sys.path: sys.path.append(module_path)
    # from poc05 import learn_grammar, params
    spaces = ''
    if kwargs['context'] == 1:
        spaces += 'c'
    else: spaces += 'd'
    if kwargs['word_space'] == 'vectors':
        spaces += 'DRK'
    else: spaces += 'ILE'
    if kwargs['grammar_rules'] == 1:
        spaces += 'c'
    else: spaces += 'd'
    details = []
    average = []
    for i,line in enumerate(lines):
        corpus = line[1]
        dataset = line[2]
        if line[3] != 0:
            kwargs['left_wall'] = 'LEFT-WALL'
            lw = 'LW'
        else:
            kwargs['left_wall'] = ''
            lw = ' -- '
        if line[4] != 0:
            kwargs['period'] = True
            dot = ' + '
        else:
            kwargs['period'] = False
            dot = ' -- '
        gen = line[5]  # none | rules | categories | both
        if gen in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if gen in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        pa = []
        pq = []
        rules = []
        for j in range(runs[0]):
            try:
                re = learn_grammar(ip, oc, og, **kwargs)
                for i in range(runs[1]):
                    a, q, qa = pqa_meter(re['grammar_file'], og, cp, rp, **kwargs)
                    pa.append(a)
                    pq.append(q)
                    rules.append(re['grammar_rules'])
                    rulestr = ' ' + str(re['grammar_rules']) + ' '
                    dline = [line[0], corpus, dataset, lw, dot, gen, spaces, rulestr, \
                        str(int(round(a,0)))+'%', str(int(round(q,0)))+'%']
                    details.append(dline)
            except:
                # print('try: re = learn_grammar(ip, oc, og, **kwargs) ⇒ except :(')
                logger.error('try: re = learn_grammar(ip, oc, og, **kwargs) ⇒ except :(')
                pa.append(0)
                pq.append(0)
                rules.append(0)
                det_line = [line[0], corpus, dataset, lw, dot, gen, spaces, ' fail ','---','---']
                details.append(det_line)
                #continue
        if len(pa) > 0:
            paa = int(round(sum(pa)/len(pa), 0))
            pqa = int(round(sum(pq)/len(pq), 0))
            non_zero_rules = [x for x in rules if x > 0]
            if len(non_zero_rules) > 0:
                average_rules_n = int(round(sum(non_zero_rules)/len(non_zero_rules), 0))
            else: average_rules_n = 0
            avg_line = [line[0], corpus, dataset, lw, dot, gen, spaces, \
                average_rules_n, str(paa)+'%', str(pqa)+'%']
            average.append(avg_line)

    return average, details


#80802 poc05.py restructured. pqa_table.py ⇒ further dev,
    #this legacy pqa_table.py renamed pqa05 to compare dev with poc05 baseline
    #FIXME:DEL with poc05 POC.0.5 after major dev
