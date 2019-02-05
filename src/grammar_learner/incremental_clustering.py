# language-learning/src/grammar_learner/incremental_clustering.py       # 90129
import sys, time, getopt, os, platform, json, traceback, logging
from copy import copy

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path: sys.path.append(module_path)
from src.grammar_learner.utl import kwa, UTC, test_stats, sec2string
from src.grammar_learner.read_files import check_path, check_dir, check_ull
# check_dir, check_corpus, check_mst_files, check_dict
from src.grammar_learner.write_files import list2file


def dict2dict(d):                                                       # 90128
    # d :: list of strings read from Link Grammar .dict file
    dct = {}
    for i in range(1, len(d) - 1):
        if len(d[i]) == 0:
            continue
        if d[i][0] == '%' and d[i + 1][-1] == ':':
            label = d[i].split()[1]
            for word in d[i + 1][:-1].split():
                dct.update({word[1:-1]: label})
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


def tag_files(**kwargs):                                                # 90129
    prefix = kwa('###', 'tag_prefix', **kwargs)
    suffix = kwa('###', 'tag_suffix', **kwargs)
    tmpath = kwa('', 'tmpath', **kwargs)
    re = {'tag_files': 'v.0.0.1 alpha 90129'}
    start = time.time()
    print('Corpus tagging started', UTC(), '\n')

    dict_path = check_path('input_grammar', '.dict', **kwargs)
    if not dict_path:
        print('Set valid "dict_path" in config.json')
    else:
        re.update({'dict_path': dict_path})
    input_path = check_path('input_parses', 'corpus', **kwargs)
    if not dict_path:
        print('Set valid "input_path" in config.json')
    else:
        re.update({'input_path': input_path})
    output_path = check_path('out_path', 'dir', **kwargs)
    if not output_path:
        print('Set valid "out_path" in config.json')
    else:
        re.update({'output_path': output_path})

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
