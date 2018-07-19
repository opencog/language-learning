#Test Grammar Learner and fill in ULL Project Plan / parses spreadshit

from ull.grammartest.optconst import *
def test_grammar_wrapped(input_path, output_grammar, runs=(1,1), **kwargs):
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


def table_amb(lines, module_path, out_dir, runs=(1,1), **kwargs):
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


def table_cds(lines, module_path, out_dir, runs=(1,1), **kwargs):
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
                #a, q, qa = test_grammar_wrapped(r['grammar_file'], og, **kwargs)
                a = 0  #tmp 80716 - no gold standard?
                q = 0  #tmp 80716 - no gold standard?
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
