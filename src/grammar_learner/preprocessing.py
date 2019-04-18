# language-learning/src/preprocessing.py  # parses cleanup & filtering  # 190411
import os
from collections import OrderedDict
from .utl import UTC, kwa


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


