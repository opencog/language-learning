#!/usr/bin/env python3
# language-learning/pipeline/ppln.py :: CLI Grammar Learner + Tester    # 81217

import sys, getopt, os, platform, json
from shutil import copy2 as copy
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path: sys.path.append(module_path)
from src.grammar_learner.utl import UTC, test_stats
from src.grammar_learner.read_files import check_dir, check_corpus
from src.grammar_learner.pqa_table import wide_rows

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
    else: config_json = args[0]

    with open(config_json) as f:
        kwargs = json.load(f)

    corpus = kwargs['corpus']; del kwargs['corpus']
    dataset = kwargs['dataset']; del kwargs['dataset']
    if 'input_parses' not in kwargs:
        kwargs['input_parses'] = '/data/' + corpus + '/' + dataset

    line = [[0, corpus, dataset, 0, 0, kwargs['rules_generalization']]]
    out_path = module_path + kwargs['out_path']
    rp = module_path + kwargs['reference']
    if 'test_corpus' in kwargs:
        cp = module_path + kwargs['test_corpus']
    else: cp = rp  # test corpus path = reference parses path
    if 'tmpath' not in kwargs:
        kwargs['tmp_dir'] = ''
    else:
        if len(kwargs['tmpath']) == 0:
            kwargs['tmp_dir'] = ''
        else:
            if 'home' in kwargs['tmpath']:
                tmpath = kwargs['tmpath']
            else: tmpath = module_path + kwargs['tmpath']
            if check_dir(tmpath, True, 'none'):
                kwargs['tmp_dir'] = tmpath
            else: kwargs['tmp_dir'] = ''

    a, _, hdr, log, rules = wide_rows(line, out_path, cp, rp, (1, 1), **kwargs)

    copy(config_json, log['project_directory'])

    print('\nGrammar learning and the learned grammar test ended', UTC())
    print(test_stats(log))
    print('Output directory:', log['project_directory'], '\n')


if __name__ == "__main__":
    main(sys.argv[1:])
