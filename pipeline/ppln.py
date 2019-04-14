#!/usr/bin/env python3
# language-learning/pipeline/ppln.py :: CLI Grammar Learner + Tester    # 81231

import sys, time, getopt, os, platform, json
from shutil import copy2 as copy
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path: sys.path.append(module_path)
from src.grammar_learner.learner import learn
from src.grammar_learner.utl import UTC, test_stats, sec2string
from src.grammar_learner.read_files import check_dir, check_corpus
from src.grammar_learner.pqa_table import wide_rows, pqa_meter
from src.grammar_learner.write_files import list2file


__version__ = '0.0.1'


def main(argv):
    """ Usage: python ppln.py config.json """
    print('\nGrammar Learner + Tester ppln v.' + __version__, 'started', UTC(),
          '| Python v.' + platform.python_version(), '\n')
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        print('''Usage: ppln <json-config-file>''')
        sys.exit()
    for opt in opts:
        if opt == '-h':
            print('''Usage: ppln <json-config-file>''')
            sys.exit()
    else:
        config_json = args[0]

    with open(config_json) as f:
        kwargs = json.load(f)

    corpus = kwargs['corpus']
    del kwargs['corpus']
    dataset = kwargs['dataset']
    del kwargs['dataset']
    if 'input_parses' not in kwargs:
        kwargs['input_parses'] = module_path + '/data/' + corpus + '/' + dataset
    else:
        if '/home/' in kwargs['input_parses']:
            kwargs['input_parses'] = kwargs['input_parses']
        else:
            kwargs['input_parses'] = module_path + kwargs['input_parses']
    if 'output_grammar' not in kwargs:
        if 'out_path' in kwargs:
            if '/home/' in kwargs['out_path']:
                kwargs['output_grammar'] = kwargs['out_path']
            else:
                kwargs['output_grammar'] = module_path + kwargs['out_path']
        else:
            print('Please set "output_grammar" or "out_path" in config.json')
            sys.exit()
    if 'tmpath' not in kwargs:
        kwargs['tmp_dir'] = ''
    else:
        if len(kwargs['tmpath']) == 0:
            kwargs['tmp_dir'] = ''
        else:
            if 'home' in kwargs['tmpath']:
                tmpath = kwargs['tmpath']
            else:
                tmpath = module_path + kwargs['tmpath']
            if check_dir(tmpath, True, 'none'):
                kwargs['tmp_dir'] = tmpath
            else:
                kwargs['tmp_dir'] = ''

    rules, re = learn(**kwargs)
    if 'error' in re:
        print('Grammar Learner error log:\n', re)
        sys.exit()

    if kwargs['linkage_limit'] > 0:
        og = module_path + kwargs['out_path']
        rp = module_path + kwargs['reference']
        if 'test_corpus' in kwargs:
            cp = module_path + kwargs['test_corpus']
        else:
            cp = rp  # test corpus path = reference parses path
        start = time.time()
        a, f1, precision, q = pqa_meter(re['grammar_file'], og, cp,rp, **kwargs)
        re.update({'grammar_test_time': sec2string(time.time() - start)})

    stats = []
    if 'grammar_learn_time' in re:
        stats.append(['Grammar learn time', re['grammar_learn_time']])
    if 'grammar_test_time' in re:
        stats.append(['Grammar test time ', re['grammar_test_time']])
    if len(stats) > 0:
        x = re['corpus_stats_file']
        list2file(stats, x[:x.rfind('/')] + '/learn_&_test_stats.txt')

    copy(config_json, re['project_directory'])
    with open(re['project_directory'] + '/grammar_learner_log.json', 'w') as f:
        f.write(json.dumps(re))

    print('\nGrammar learning and the learned grammar test ended', UTC())
    print(test_stats(re))
    print('Output directory:', re['project_directory'], '\n')


if __name__ == "__main__":
    main(sys.argv[1:])


# Comments:

# 81231 v.0.01
# 90129 2nd test with updated .dict: LG 5.4.4 & 5.5.1 options, no filename