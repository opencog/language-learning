# language-learning/src/grammar_learner/incremental_clustering.py       # 190409
import sys, time, getopt, os, platform, json, traceback, logging
from copy import copy
from shutil import copy2 as file_copy
from ..common import handle_path_string
from .utl import kwa, UTC, test_stats, sec2string
from .read_files import check_path, check_dir, check_ull
from .learner import learn
from .pqa_table import params, pqa_meter
from ..grammar_tester import test_grammar
from .write_files import list2file
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path: sys.path.append(module_path)
# from src.grammar_learner.utl import kwa, UTC, test_stats, sec2string
# from src.grammar_learner.read_files import check_path, check_dir, check_ull
# check_dir, check_corpus, check_mst_files, check_dict
# from src.grammar_learner.learner import learn


def dict2dict(d):                                                       # 90205
    # d :: list of strings read from Link Grammar .dict file
    dct = {}
    for i in range(1, len(d) - 1):
        if len(d[i]) == 0:
            continue
        elif d[i][0] == '%' and d[i + 1][-1] == ':':
            label = str(d[i].split()[1]).lower()                        # 90201
            for word in d[i + 1][:-1].split():
                dct.update({word[1:-1]: label})  # 90128 v.0 + 90205:
                # dct.update({word[1:-1].replace('.', '@'): label})     # 190408
                # '@' is replaced with '.' while learning grammar (WSD)
                # 190408: WSD ⇒ optional, not to be used soon ⇒ snooze...
    return dct


def tag_cats(s, dct, prefix = '###', suffix = '###'):                   # 90128
    # s     :: list of strings read from .ull parse file f.read().splitlines()
    # dct   :: { word: ###AB### }
    tagged: list = s[:]  # tagged = copy(s)
    sentence = True
    for i in range(0, len(s)):
        lst: list = s[i].split()
        if len(lst) == 0:
            sentence = True
        elif sentence:
            tagged[i] = ' '.join([prefix + dct[x] + suffix
                                  if x in dct else x for x in lst])
            sentence = False
        else:
            if len(lst) == 4 and lst[0].isdigit() and lst[2].isdigit():
                for j in [1, 3]:
                    if lst[j] in dct:
                        lst[j] = prefix + dct[lst[j]] + suffix
                tagged[i] = ' '.join(lst)

    return '\n'.join(tagged)


def tag_files(**kwargs):                                                # 90201
    prefix = kwa('###', 'tag_prefix', **kwargs)
    suffix = kwa('###', 'tag_suffix', **kwargs)
    tmpath = kwa('', 'tmpath', **kwargs)
    re = {'tag_files': 'v.0.0.2.90201'}
    start = time.time()
    #-print('Corpus tagging started', UTC(), '\n')

    dict_path = check_path('input_grammar', '.dict', **kwargs)
    if not dict_path:
        print('Set valid "dict_path" in config.json')
    else:
        re.update({'tagger_dict_path': dict_path})
    input_path = check_path('input_parses', 'corpus', **kwargs)
    if not input_path:
        print('Set valid "input_parses" path in config.json')
    else:
        re.update({'tagger_input_path': input_path})
    if 'out_path' in kwargs:
        output_path = check_path('out_path', 'dir', **kwargs)
    else:
        output_path = check_path('output_grammar', 'dir', **kwargs)
    if not output_path:
        print('Set valid "out_path" or "output_grammar" in config.json')
    else:
        re.update({'tagger_output_path': output_path})

    if None in [dict_path, input_path, output_path]:
        print('Wrong config.json:', kwargs)
        re.update({'tag_files_error': 'wrong config.json'})
        return re  # TODO: throw exception?

    # Create directory for tagged ull files
    tagged_ull_dir = output_path + '/tagged_ull/'
    if not check_dir(tagged_ull_dir, True, 'max'):
        print('Output directory error:', tagged_ull_dir)
        re.update({'tag_files_error':
                   'output directory error: ' + tagged_ull_dir})
        return re  # TODO: throw exception?

    # Create { word: label } dictionary
    with open(dict_path, 'r') as f:
        d = f.read().splitlines()
    dct = dict2dict(d)

    # Process input .ull files, store tagged .ull files with the same name
    for filename in os.listdir(input_path):
        file = input_path + '/' + filename
        # file = check_path(input_path + '/' + filename, 'ull', **kwargs)
        if not check_ull(file):  # TODO: check file
            print('Error in LG dictionary', file)
            re.update({'tag_files_error':
                       'Link Grammar dict error: ' + file})
            return re  # TODO: throw exception?
        else:
            with open(file, 'r') as f:
                s = f.read().splitlines()
            tagged: str = tag_cats(s, dct, prefix, suffix)
            with open(tagged_ull_dir + '/' + filename, 'w') as f:
                f.write(tagged)

    re.update({'category_tagging_time': sec2string(time.time() - start)})
    return re


def dict2lists(kd, **kwargs):                                           # 90131
    prefix = kwa('###', 'tag_prefix', **kwargs)
    suffix = kwa('###', 'tag_suffix', **kwargs)
    dct = {}
    for i in range(1, len(kd) - 1):
        if len(kd[i]) == 0: continue
        if kd[i][0] == '%' and kd[i+1][-1] == ':':
            tag = '"' + prefix + kd[i].split()[1].lower() + suffix + '"'
            dct.update({tag: kd[i+1][:-1].split()})
    return dct


def decode_dict(d, kd):                                                 # 90131
    dcd = d[:]
    for i in range(0, len(dcd)-1):
        if len(d[i]) == 0: continue
        if d[i][0] == '%' and d[i + 1][-1] == ':':
            lst: list = d[i + 1][:-1].split()
            if len(lst) > 0:
                x = []
                for y in lst:
                    if y in kd: x.extend(kd[y])
                    else: x.append(y)
            dcd[i+1] = ' '.join(x) + ':'  # sorted(set(lst))
    return '\n'.join(dcd)


def decode_cat_tree(tree, lg_dict, **kwargs):
    if type(lg_dict) is str: kd = lg_dict.split('\n')
    elif type(lg_dict) is list: kd = lg_dict
    # TODO: else raise error

    prefix = kwa('###', 'tag_prefix', **kwargs)
    suffix = kwa('###', 'tag_suffix', **kwargs)
    dct = {}
    for i in range(1, len(kd) - 1):
        if len(kd[i]) == 0: continue
        if kd[i][0] == '%' and kd[i+1][-1] == ':':
            tag = prefix + kd[i].split()[1].lower() + suffix
            tokens = [x[1:-1] for x in kd[i+1][:-1].split()]
            dct.update({tag: tokens})
    tree_lines = tree.split('\n')
    decoded_tree_lines = []
    for line in tree_lines:
        lst = line.split('\t')
        dlst = lst[:4]
        #-decoded_cats = 'decode!'  # lst[4]      # TODO: decode
        if lst[4] in dct:
            dlst.append(' '.join(dct[lst[4]]))
        else:
            dlst.append(lst[4])
        dlst.extend(lst[5:])
        decoded_tree_lines.append('\t'.join(dlst))
    decoded_tree = '\n'.join(decoded_tree_lines)
    return decoded_tree


def tag_learn_test(**kwargs):                                           # 90201
    # tag_files args:
    input_path: str = kwargs['input_parses']
    output_path: str = kwargs['output_grammar']  # ['out_path'] ?
    corpus: str = kwargs['output_grammar']
    cp: str

    log = {}

    if 'input_grammar' not in kwargs:
        rulez, re01 = learn(**kwargs)
        log.update(re01)
        new_dict_path = re01['grammar_file']

    else:  # tag and learn
        # print('else: tag and learn')

        #?kwargs['out_path'] = kwargs['output_grammar'] # used in tag_files only
        # if 'out_path' in kwargs:
        #   out_path : str = kwargs['out_path']
        #   del kwargs['out_path']  # tag_files uses kwargs['output_grammar'] instead
        key_dict_path: str = kwargs['input_grammar']  # dict for tagging
        re02 = tag_files(**kwargs)
        log.update(re02)

        #-kwargs['input_parses'] = re1['tagger_output_path'] + '/tagged_ull'
        kwargs['input_parses'] = output_path + '/tagged_ull'
        check_dir(kwargs['input_parses'], False, 'max')

        #-kwargs['output_grammar'] = kwargs['out_path']
        rulez, re03 = learn(**kwargs)   # rulez: dict FIXME: return
        log.update(re03)

        # Decode .dict:
        new_dict_path = re03['grammar_file']
        with open(new_dict_path, 'r') as f:
            d: list = f.read().splitlines()  # TODO? split at dict2list?
        tagged_dict_path = file_copy(new_dict_path, new_dict_path + '.tagged')

        with open(key_dict_path, 'r') as f:
            kd: list = f.read().splitlines()  # TODO? split at dict2list?
        clusters: dict = dict2lists(kd, **kwargs)
        with open(new_dict_path, 'w') as f:
            f.write(decode_dict(d, clusters))
        # TODO: single def to decode dict, input -- 2*strings:
        # with open(key_dict_path, 'r') as f: kd = f.read()  # string
        # with open(new_dict_path, 'r') as f: d = f.read()  # string
        # decoded_dict: str = decode_dict_new(d, kd)
        # decoded

        #-check:
        #-with open(new_dict_path, 'r') as f: tmp = f.read().splitlines()
        #-print(tmp[-7:])

        # TODO: decode cat_tree.txt
        cat_tree_file = re03['cat_tree_file']
        with open(cat_tree_file, 'r') as f:
            tree = f.read()
        tagged_cat_tree_path = file_copy(
            cat_tree_file, cat_tree_file + '.tagged')
        with open(cat_tree_file, 'w') as f:
            f.write(decode_cat_tree(tree, kd, **kwargs))

    # TODO: Test Grammar with decoded .dict
    # pa, f1, p, pq: parse-ability, F-measure, precision, parse quality
    pa, f1, p, pq = pqa_meter(new_dict_path, '', '', '', **kwargs)
    # op,cp,rp = '' » use kwargs['out_path'], corpus_path, reference_path
    # TODO: log.update(a, f1, p, q)
    # print('pa, f1, p, pq:', pa, f1, p, pq)
    # TODO: replace pqa_meter with a local function: re = pqa(**kwargs)

    # TODO: decode & return rulez? return .dict converted to a string?
    # TODO: return line []?
    return log['grammar_rules'], pa, f1, log  # rulez, log


def iterate(**kwargs):                                                  # 90204
    re = {'iterate_started': UTC()[:10]}
    language_learning_dir = os.path.abspath(os.path.join('..'))
    print('language_learning_dir:', language_learning_dir)
    if language_learning_dir not in sys.path:
        sys.path.append(language_learning_dir)
    module_path = kwa(language_learning_dir, 'module_path', **kwargs)
    corpus = kwa('POC-English-Amb', 'corpus', **kwargs)
    dataset = kwa('MST-fixed-manually', 'dataset', **kwargs)

    out_grmr = kwa(None, 'output_grammar', **kwargs)
    out_path = kwa(None, 'out_path', **kwargs)
    if out_path is None:
        if out_grmr is not None:
            out_path = out_grmr
        else: out_path = module_path

    input_path = kwa(None, 'input_path', **kwargs)   # TODO: check paths?
    inp_grmr = None
    if 'input_grammar' in kwargs:
        inp_grmr = kwargs['input_grammar']
        del kwargs['input_grammar']
    ip, oc, prj_dir = params(corpus, dataset, module_path, out_path, **kwargs)
    if input_path is None: kwargs['input_parses'] = ip
    else: kwargs['input_parses'] = input_path
    #kwargs['out_path'] = prj_dir
    #kwargs['output_grammar'] = kwargs['out_path']

    if 'reference_path' not in kwargs:
        kwargs['reference_path'] = kwargs['input_parses']
    if 'corpus_path' not in kwargs:
        kwargs['corpus_path'] = kwargs['reference_path']

    table = [['Iteration', 'N clusters', 'PA', 'F1']]
    responses = {}  # FIXME: DEL or return?
    np = 1000000

    iterations = kwa(7, 'iterations', **kwargs)
    for i in range(1, iterations + 1):
        kwargs['output_grammar'] = prj_dir + '/iteration_' + str(i)
        kwargs['out_path'] = kwargs['output_grammar']  # out_path for pqa_meter
        try:
            n, pa, f1, re = tag_learn_test(**kwargs)
            print(n, 'clusters: PA =', str(int(round(pa * 100, 0)))+'%',
                  'F1 =', round(f1, 2))
            responses.update({i: re})
            table.append([str(i), str(n), str(int(round(pa * 100, 0))) + '%,',
                          str(round(f1, 2))])
            kwargs['input_grammar'] = re['grammar_file']
        except: break
        if n < 4: break
        elif n == np:           # TODO '>=' ⇒ '==' 80209
            return table, re
        else: np = n

    # TODO: copy last valid grammar to root dir

    if out_path is not None: kwargs['out_path'] = out_path
    if out_grmr is not None: kwargs['output_grammar'] = out_grmr
    if inp_grmr is not None: kwargs['input_grammar'] = inp_grmr

    return table, re


def new_pqa_meter(dict_path, op, cp, rp, **kwargs):  # TODO
    # 90201 copied pqa_table.py/pqa_meter (modified 90131)
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

    print('\npqa_meter grammar_path:\n', grammar_path,
          '\noutput_path:\n', output_path, '\n')

    template_path = handle_path_string("tests/test-data/dict/poc-turtle") #FIXME:WTF?
    linkage_limit = kwargs['linkage_limit'] \
                    if 'linkage_limit' in kwargs else 1000
    if kwargs['linkage_limit'] == 0:
        return 0.0, 0.0, 0.0, 0.0  # table_rows: get grammar for further tests
    options = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY | BIT_ULL_IN  # | BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
    # BIT_ULL_IN :: use ull parses as test corpus
    # BIT_CAPS  :: preserve caps in parses, process inside Grammar Learner
    pa, f1, precision, recall = test_grammar(corpus_path, output_path,
                                             dict_path, grammar_path,
                                             template_path, linkage_limit,
                                             options, reference_path)
    return float(pa), float(f1), float(precision), float(recall)


# Comments:

# 1901 29-30 dict2dict, tag_cats, tag_files » pipeline/category_tagger
# 190409 WSD off: [x] dct.update({word[1:-1].replace('.', '@'): label})
'''ATTN: This is still a stub result of 2 days idea check'''
# FIXME: There is an issue somewhere in tagging or filtering or input parses
#  - tagged dictionaries contain non-tagged words
#  - http://langlearn.singularitynet.io/data/clustering_2019/html/Iterative-Clustering-ILE-POCE-CDS-2019-02-28.html
