# language-learning/src/preprocessing.py  # parses cleanup & filtering  # 190412
from collections import OrderedDict
from .read_files import check_ull
from .preprocessing import read_files, parse_ull


def _compare_lg_dicts_(**kwargs):
    """ compares test and reference Link Grammar .dict files
    :param kwargs: '
    :return:        (precision, recall, F1)
    """
    re = OrderedDict([('_compare_lg_dicts_', 'v.0.1.1 190412')])
    # Preserve input_path
    if 'input_path' in kwargs: input_path = kwargs['input_path']
    else: input_path = ''

    # Get links for the reference_ull » ref_set: set of links in reference file
    if 'reference_path' in kwargs: # and check_ull(kwargs['reference_path']):
        kwargs['input_path'] = kwargs['reference_path']
        # ull_string: ull parses file(s) read as a string with '\n' delimited lines
        ull_string, re_ = read_files(**kwargs)
        # TODO: re.update(re_)  # TODO: identify ref / test sets!
        # sentences: [[str, str, ...], ...]; sl: sentence links: [(1, 2, 1.0), ...]
        sentences, slinks, re_ = parse_ull(ull_string, **kwargs)
        re.update([('reference_sentences', len(slinks))])
        # TODO: re.update(re_)
        ref_set = set([tuple([i+1, l[0], l[1]])
                       for i, sl in enumerate(slinks) for l in sl])
    else: return 0.0, 0.0, 0.0, {'error': 'wrong kwargs["reference_path"]',
                                 'reference_path': kwargs['reference_path']}

    # Get links for the test_ull » ref_set: set of links in reference file
    if 'test_path' in kwargs and check_ull(kwargs['test_path']):
        kwargs['input_path'] = kwargs['test_path']
        ull_string, re_ = read_files(**kwargs)
        # TODO: re.update(re_)
        sentences, slinks, re_ = parse_ull(ull_string, **kwargs)
        re.update([('test_ull_sentences', len(slinks))])
        # TODO: re.update(re_)
        tst_set = set([tuple([i+1, l[0], l[1]])
                       for i, sl in enumerate(slinks) for l in sl])
    else: return 0.0, 0.0, 0.0, {'error': 'wrong kwargs["test_path"]',
                                 'test_path': kwargs['test_path']}

    true_positives = tst_set & ref_set
    precision = len(true_positives) / len(tst_set)
    recall = len(true_positives) / len(ref_set)
    f1 = 2 * precision * recall / (precision + recall)
    re.update([('precision', precision), ('recall', recall), ('F1', f1)])
    # Restore preserved input_path
    if 'input_path' != '': kwargs['input_path'] = input_path

    return precision, recall, f1, re
