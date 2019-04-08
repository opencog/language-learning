# language-learning/src/grammar_learner/utl.py                          # 190408
import os, sys, time, datetime,  itertools, operator, numpy as np
from collections import Counter, OrderedDict
from .read_files import check_mst_files

def UTC():
    return str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))


def round_float(x, n_digits):
    if type(x) == float:
        if abs(x) < 0.5 * 10 ** (-n_digits):
            return 0.0
        else:
            return round(x, n_digits)
    else:
        return x

def round1(x): return round_float(x, 1)
def round2(x): return round_float(x, 2)
def round3(x): return round_float(x, 3)
def round4(x): return round_float(x, 4)
def round5(x): return round_float(x, 5)


def timer(string, t0 = 0):
    t1 = time.time()
    if t0 < 0.01:
        print(UTC(), '::', string)
        dt = 0
    else:
        dt = t1 - t0
        if dt < 1:
            dt = round(dt, 2)
            print(UTC(), '::', string, 'in', dt, 'seconds')
        elif dt < 300:
            dt = int(round(dt, 0))
            print(UTC(), '::', string, 'in', dt, 'seconds')
        else:
            dt = int(round(dt, 0))
            print(UTC(), '::', string, 'in', int(round(dt / 60, 0)), 'minutes')
    return t1, dt


def kwa(v, k, **kwargs):
    return kwargs[k] if k in kwargs else v


def sec2string(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def test_stats(log):                                                    # 90104
    if 'cleaned_words' in log:
        re = 'Cleaned dictionary: ' + str(log['cleaned_words']) + ' words, '
    else:
        re = ''
    if 'grammar_learn_time' in log:
        re = re + 'grammar learn time: ' + str(log['grammar_learn_time'])
        if 'grammar_test_time' in log:
            re = re + ', '
    if 'grammar_test_time' in log:
        re = re + 'grammar test time: ' + str(log['grammar_test_time'])

    return re


def _filter_parses_(**kwargs):  # 2019-04-06 stub  TODO: restructure    # 190406
    """ creates .ull parses dile with sentences consisting of words
    :param kwargs: ['input_parses', 'output_filtered_ull', 'min_word_count']
    :return:
    """
    out_file = kwargs['output_filtered_ull']
    min_word_count = kwa(1, 'min_word_count', **kwargs)
    re = OrderedDict([('filter_parses', UTC())])
    files, re_ = check_mst_files(kwargs['input_parses'], 'none')
    re.update(re_)
    us = ''  # us: ull string
    for file in files:
        with open(file, 'r') as f: s = f.read()
        if len(us) > 0:
            if us[-1] != '\n': us += '\n'
        us += s
        if us[-1] != '\n': us += '\n'
    re.update([('read_files', len(files)),
               ('read_parses_lines', us.count('\n') - us.count('\n\n'))])
    sentences = []
    slinks = []
    sentence = []
    sentence_links = []
    for ll in us.splitlines():
        l = ll.split()
        if len(l) in [4,5] and l[0].isdigit() and l[2].isdigit():
            if len(sentence) > 0 and l[0] != '0':
                if len(l) == 4:
                    sentence_links.append((int(l[0]), int(l[2]), 1.0))
                elif l[4].replace('.', '').replace(',', '').isdigit():
                    sentence_links.append((l[0], l[2], float(l[4].replace(',', ''))))
        elif len(l) > 0:
            if len(sentence) > 0:
                sentences.append([w for w in sentence])
                slinks.append(sentence_links)
            sentence = l
            sentence_links = []
    re.update([('parsed_sentences', len(sentences)), ('parsed_links', len(slinks))])
    # Count words
    dct = dict(Counter(x for x in list(itertools.chain.from_iterable(sentences))))
    # TODO: remove stop words here?
    tuples = sorted(dct.items(), key=lambda x: (-x[1], x[0]))
    words = np.asarray([''] + [x[0] for x in tuples])
    word_counts = np.asarray([0] + [x[1] for x in tuples])
    re.update([('words_in_sentences', len(words))])
    # Tokenize sentences
    trash = kwa([], 'stop_words', **kwargs)
    word_index = {w: i for i,w in enumerate(list(words))}
    stop_words = [''] + trash
    removed_word_ids = [word_index.pop(w) for w in stop_words if w in word_index]
    ts = [[word_index[w] if w in word_index else 0 for w in s] for s in sentences]
    re.update([('removed_word_ids', removed_word_ids)])
    # Filter sentences
    fwn = len(word_counts[word_counts > min_word_count])
    fsn = [i for i,s in enumerate(ts) if max(s) < fwn]
    re.update([('filtered_sentences', len(fsn))])
    # Restore filtered parses (fp) ull string
    if len(fsn) == 0: fsn = [i for i,x in enumerate(ts)]
    ss = [[words[y] for y in ts[x]] for x in fsn]
    li = [[y for y in slinks[x]] for x in fsn]
    ls = [[[y[0], ss[i][y[0]-1], y[1], ss[i][y[1]-1], y[2]] for y in x]
          for i,x in enumerate(li)]
    fsl = []
    for i,s in enumerate(ss):
        fsl.append(s)
        fsl.extend(ls[i])
        fsl.append([''])
    fp = '\n'.join([' '.join([str(w) for w in l]) for l in fsl])
    re.update([('filtered_parses_lines', us.count('\n') - us.count('\n\n'))])
    # Save filtered parses
    with open(out_file, 'w') as f: f.write(fp)
    re.update([('filtered_ull_path', out_file)])
    return fp, re


# Notes

# 181231 cleanup
# 190104 update test_stats
# 190406 filter_parses  TODO: restructure...
