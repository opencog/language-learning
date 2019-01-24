#!/usr/bin/env python3
# language-learning/pipeline/tstr.py :: CLI Grammar Tester              # 90123

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
    """ Usage: python tstr.py config.json """
    print('\nGrammar Tester v.' + __version__, 'started', UTC(),
          '| Python v.' + platform.python_version(), '\n')
    try:
        opts, args = getopt.getopt(argv, "h", ["help"])
    except getopt.GetoptError:
        print('''Usage: tstr <json-config-file>''')
        sys.exit()
    for opt in opts:
        if opt == '-h':
            print('''Usage: tstr <json-config-file>''')
            sys.exit()
    else:
        config_json = args[0]

    with open(config_json) as f:
        kwargs = json.load(f)

    re = {}

    if 'input_grammar' in kwargs:  # Test .dict file    # 90123
        ig = module_path + kwargs['input_grammar']
        og = module_path + kwargs['out_path']           # og: output grammar
        rp = module_path + kwargs['reference']          # rp: reference path
        if 'test_corpus' in kwargs:
            cp = module_path + kwargs['test_corpus']    # cp: corpus path
        else:
            cp = rp  # test corpus path = reference parses path
        print('Input grammar:', ig, '\nOutput directory:', og)
        if check_dir(og, True, 'max'):
            print('Grammar test started', UTC(), '\n')
            start = time.time()
            a, f1, precision, q = pqa_meter(ig, og, cp, rp, **kwargs)
            re.update({'grammar_test_time': sec2string(time.time() - start)})
        else:
            print('Output path error:', og)
    else:
        print('Please set "input grammar" in config.json')
        sys.exit()

    stats = []
    if 'grammar_test_time' in re:
        stats.append(['Grammar test time ', re['grammar_test_time']])
    if len(stats) > 0:
        list2file(stats, og + '/test_stats.txt')

    copy(config_json, og)
    #with open(re['project_directory'] + '/grammar_learner_log.json', 'w') as f:
    #    f.write(json.dumps(re))

    print('\nGrammar learning and the learned grammar test ended', UTC())
    #print(test_stats(re))
    #print('Output directory:', re['project_directory'], '\n')
    print(f'PA = {int(round(a*100,0))}%, PQ = {int(round(q*100,0))}%, '
          f'F1 = {round(f1,2)}')


if __name__ == "__main__":
    main(sys.argv[1:])


# Comments:

# 90123 test old dicts -- based on ppln.py v.81231
