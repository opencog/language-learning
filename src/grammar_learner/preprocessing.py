# language-learning/src/preprocessing.py  # parses cleanup & filtering  # 190417
import os
from collections import OrderedDict
from .utl import UTC, kwa
from .read_files import check_dir, check_mst_files
from .pparser import lines2links
from .corpus_stats import corpus_stats
from .write_files import list2file, save_link_grammar, save_cat_tree


def read_files(**kwargs):
    """ reads files to a test string
    :param kwargs:  kwargs['input_path']: file path or dir with input files
    :return:        (us, re)
                    us: ull string ~ ull parses as a single string, '\n' delimited lines
    """
    files = []
    if os.path.isfile(kwargs['input_path']):
        files.append(kwargs['input_path'])
    elif os.path.isdir(kwargs['input_path']):
        for root, dirs, fls in os.walk(kwargs['input_path']):
            for f in fls:
                files.append(os.path.join(root, f))
    else: return '', {}
    # us: ull string ~ ull parses file as a string, lines delimited by '\n'
    us = ''
    for file in files:
        with open(file, 'r') as f :  s = f.read()
        if len(us) > 0:
            if us[-1] != '\n' :  us += '\n'
        us += s
        if us[-1] != '\n' :  us += '\n'
    # TODO: cleanup here or in a separate constructor?
    re = OrderedDict([('read_files', UTC()),
                      ('input_path', kwargs['input_path']),
                      ('read_files_number', len(files)),
                      ('read_text_lines', us.count('\n') - us.count('\n\n'))])
    return us, re


def parse_ull(ullstring, **kwargs):
    """ parses ull string to a list of sentences [str], sentence links [[(int)]]
    :param ullstring:   ull string ~ ull parses as a single string, '\n' delimited lines
    :param kwargs:      kwargs['link_weights']: True ⇒ use stats in output parses
    :return:            (sentences, slinks, re)
    """
    link_weights = kwa(False, 'link_weights', **kwargs)
    sentences = []
    slinks = []
    sentence = []
    sentence_links = []
    for ll in ullstring.splitlines():
        l = ll.split()
        if len(l) in [4,5] and l[0].isdigit() and l[2].isdigit():
            if len(sentence) > 0 and l[0] != '0':
                if not link_weights:
                    sentence_links.append((int(l[0]), int(l[2])))
                else:
                    if len(l) == 4:
                        sentence_links.append((int(l[0]), int(l[2]), 1.0))
                    elif l[4].replace('.', '').replace(',', '').isdigit():
                        sentence_links.append((l[0], l[2], float(l[4].replace(',', ''))))
                    else: sentence_links.append((int(l[0]), int(l[2]), 1.0))
        else:
            if len(sentence) > 0:
                sentences.append([w for w in sentence])
                slinks.append(sentence_links)
                sentence = []
            else: sentence = l
            sentence_links = []

    re = OrderedDict([('parsed_sentences', len(sentences)),
                      ('parsed_links', len(slinks))])
    return sentences, slinks, re


def filter_links(files, **kwargs):                                      # 190417
    """ parses input files, filters and re
    :param files:   list of paths to input files
    :param kwargs:  defined in kwa below
    :return:        (links, re): DataFrame, {}
    """
    parse_mode = kwa('lower', 'parse_mode', **kwargs)  # 'casefold' » default?
    wsd_symbol = kwa('', 'wsd_symbol', **kwargs)
    output_grammar = kwargs['output_grammar']
    if 'project_directory' in kwargs:
        prj_dir = kwargs['project_directory']
    elif os.path.isdir(output_grammar):
        prj_dir = output_grammar
    elif os.path.isfile(output_grammar):
        prj_dir = os.path.dirname(output_grammar)
    else:  # create prj_dir = output_grammar
        if check_dir(output_grammar, True, 'none'):
            prj_dir = output_grammar

    output_statistics = kwa('', 'output_statistics', **kwargs)
    if output_statistics != '':
        if os.path.isfile(output_statistics):
            corpus_stats_file = output_statistics
        elif os.path.isdir(output_statistics):
            corpus_stats_file = output_statistics + '/corpus_stats.txt'
        else:
            corpus_stats_file = prj_dir + '/corpus_stats.txt'
    else:
        corpus_stats_file = prj_dir + '/corpus_stats.txt'

    re = OrderedDict()
    lines = []  # learner line 91
    for i, file in enumerate(files):
        with open(file, 'r') as f: lines.extend(f.readlines())
        if len(lines[-1]) > 0: lines.append('')
    if parse_mode == 'lower':
        lines = [' '.join([w.lower() if w != '###LEFT-WALL###'
                           else w for w in l.split()]) for l in lines]
    elif parse_mode == 'casefold':
        lines = [' '.join([w.casefold() if w != '###LEFT-WALL###'
                           else w for w in l.split()]) for l in lines]
    # WSD: word sense disambiguation symbol resolution:
    if wsd_symbol != '':                                                # 190408
        lines = [' '.join([w[0] + w[1:-1].replace(wsd_symbol, '.') + w[-1]
                           if len(w) > 2 else w
                           for w in l.split()]) for l in lines]

    if 'corpus_stats' in corpus_stats(lines):
        raw_corpus_stats = corpus_stats(lines)['corpus_stats']
        if type(raw_corpus_stats) is list:
            re.update({'raw_corpus_stats': raw_corpus_stats})
            list2file(raw_corpus_stats, prj_dir + '/raw_corpus_stats.txt')
            re.update({'raw_corpus_stats_file': prj_dir + '/raw_corpus_stats.txt'})

    links, re_ = lines2links(lines, **kwargs)
    re.update(re_)
    # Empty filtered df with 'max_sentence_length', 'max_unparsed_words'
    if len(links) < 1:
        re.update({'filtering error': 'empty_filtered_dataset'})
        return {}, re

    if 'corpus_stats' in re:
        list2file(re['corpus_stats'], corpus_stats_file)
        re.update({'corpus_stats_file': corpus_stats_file})
    # else:  # FIXME: raise error / assert ?
    #    return {'error': 'input_files'}, re

    return links, re
