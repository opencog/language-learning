#Test Grammar Learner to fill in ULL Project Plan Parses spreadshit
import os, sys, time

from ull.grammartest.optconst import *
def test_grammar_wrapped(input_path, output_grammar, runs=(1,1), **kwargs): #TODO:DEL after paq_meter
    # input_path, output_grammar ~ standard
    from ull.common import handle_path_string
    from ull.grammartest import test_grammar
    #-from ull.grammartest.optconst import * # import * only allowed at module level
    corpus_path   = kwargs['test_corpus']
    output_path   = output_grammar
    dict_path     = input_path
    grammar_path  = output_grammar
    template_path = handle_path_string("tests/test-data/dict/poc-turtle")
    linkage_limit = kwargs['linkage_limit'] #100
    options = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY #| BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
    reference_path = kwargs['reference_path']
    pa, pq, pqa = test_grammar(corpus_path, output_path, dict_path, \
        grammar_path, template_path, linkage_limit, options, reference_path)
    return pa, pq, pqa


def pqa_meter(input_path, output_grammar, corpus_path, reference_path, runs=(1,1), **kwargs):
    #80720 test_grammar_wrapped 2.0
    from ull.common import handle_path_string
    from ull.grammartest import test_grammar
    #-from ull.grammartest.optconst import * # import * only allowed at module level
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


def table_amb(lines, module_path, out_dir, runs=(1,1), **kwargs): # v.<80720 #TODO:DEL after _damb
    from src.grammar_learner.poc05 import learn_grammar, params #, parse_metrics, run_learn_grammar
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
        if corpus == 'POC-English-disAmb':
            kwargs['test_corpus'] = module_path + \
                '/data/POC-English-Amb/poc_english.txt'
                #'/data/POC-English-disAmb/EnglishPOC.txt_disamb_gold'  # used before 80717 = wrong!
            kwargs['reference_path'] = module_path + \
                '/data/POC-English-Amb/poc-english_ex-parses-gold.txt'
                #'/data/POC-English-disAmb/EnglishPOC.txt_disamb_gold'
        else:
            kwargs['test_corpus'] = module_path + \
                '/data/POC-English-Amb/poc_english.txt'
            kwargs['reference_path'] = module_path + \
                '/data/POC-English-Amb/poc-english_ex-parses-gold.txt'
        if kwargs['left_wall'] == 'LEFT-WALL':
            lw = 'LW'
        else: lw = ' -- '
        if kwargs['period']:
            dot = ' + '
        else: dot = ' -- '
        gen = line[3]  # none | rules | categories | both
        if line[3] in ['rules','both']:
            kwargs['rules_generalization'] = 'jaccard'
        else: kwargs['rules_generalization'] = 'off'
        if line[3] in ['categories','both']:
            kwargs['categories_generalization'] = 'jaccard'
        else: kwargs['categories_generalization'] = 'off'
        if kwargs['grammar_rules'] == 1 and gen != 'none': continue

        ip, oc, og = params(corpus, dataset, module_path, out_dir, **kwargs)
        pa = []
        pq = []
        rules = []
        for j in range(runs[0]):
            r = learn_grammar(ip, oc, og, **kwargs)
            for i in range(runs[1]):
                #a, q, lg_parse_path = parse_metrics(r['grammar_file'], **kwargs)
                a, q, qa = test_grammar_wrapped(r['grammar_file'], og, **kwargs)
                pa.append(a)
                pq.append(q)
                rules.append(r['grammar_rules'])
                rulestr = ' ' + str(r['grammar_rules']) + ' '
                line = [line[0], corpus, dataset, lw, dot, gen, spaces, rulestr, \
                    str(int(round(a,0)))+'%', str(int(round(q,0)))+'%'] #, \
                    #-str(int(round(qa, 0)))+'%']  #80713: delete pqa
                    #-str(a)+'%', str(q)+'%', str(int(round(a*q/100, 0)))+'%']
                details.append(line)
        paa = int(round(sum(pa)/len(pa), 0))
        pqa = int(round(sum(pq)/len(pq), 0))
        rules_avg = int(round(sum(rules)/len(rules), 0))
        avg = [line[0], corpus, dataset, lw, dot, gen, spaces, rules_avg, \
            str(paa)+'%', str(pqa)+'%'] #, str(int(round(paa*pqa/100, 0)))+'%']
        average.append(avg)
    return average, details


def table_damb(lines, out_dir, cps=(0,0), rps=(0,0), runs=(1,1), **kwargs):  #-lines, module_path, 
    #80720: table_amb 2.0: module_path, corpus_path, test_path built-in
    # cps,rps: tuples len=2 corpus_paths, reference_paths for Amb and disAmb corpora
    module_path = os.path.abspath(os.path.join('..'))
    if module_path not in sys.path: sys.path.append(module_path)
    from src.grammar_learner.poc05 import learn_grammar, params
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
    # cp,rp: corpus_path, rp: reference_path for grammar tester
    module_path = os.path.abspath(os.path.join('..'))
    if module_path not in sys.path: sys.path.append(module_path)
    from src.grammar_learner.poc05 import learn_grammar, params
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
            str(paa)+'%', str(pqa)+'%'] #, str(int(round(paa*pqa/100, 0)))+'%']
        average.append(avg)
    return average, details
