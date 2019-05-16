import sys
import os
import random
import logging
import traceback
# from decimal import Decimal

from typing import Tuple, List, Dict

from ..common.dirhelper import traverse_dir_tree
from ..common.parsemetrics import ParseQuality
from ..common.optconst import *
from .parsestat import parse_quality
from .psparse import parse_postscript, get_link_set
from .lgmisc import print_output
from linkgrammar import ParseOptions, Dictionary, Sentence, Linkage


__all__ = ['load_ull_file', 'get_parses', 'eval_parses', 'compare_ull_files', 'EvalError']


PARSE_SENTENCE = 0
PARSE_LINK_SET = 1
PARSE_IGNORED = 2

logger = logging.getLogger(__name__)


class EvalError(Exception):
    pass


def load_ull_file(filename: str):
    """
        Loads a data file
    """
    with open(filename, "r", encoding="utf-8-sig") as file:
        data = file.read()

    return data


def get_parses(data, ignore_wall: bool = True, sort: bool = False) -> List[Tuple[str, set, int]]:
    """
        Separates parses from data into format:
        [
            [ <sentence>, <set-of-link-tuples>, <ignored-link-count> ]
            ...
        ]
        <sentence> - text string
        <set-of-link-tuples> - set of tuples, where each tuple has two token indexes
        <ignored-link-count> - integer value representing the number links which were not added to the set of tuples.

        Each list is splitted into tokens using space.
    """
    parses: List[Tuple[str, set, int]] = []

    for bulk in data.split("\n\n"):

        if not len(bulk):
            continue

        parse = []
        line_count = 0

        for line in bulk.split("\n"):

            if line_count == 0:
                parse.append((((line.replace("[", "")).replace("]", "")).replace("\n", "")).strip())
                parse.append(set())
                parse.append(int(0))

            elif len(line):
                link = line.split()

                assert len(link) in [4, 5], "The line appears not to be a link: '{}'".format(line)

                # Do not add LW and period links to the set if 'ignore_wall' is specified
                if ignore_wall and (link[1] == "." or link[3] == "." or link[1] == "[.]" or link[3] == "[.]"
                                    or link[1].startswith(r"###") or link[3].startswith(r"###")):

                    parse[PARSE_IGNORED] += 1  # count ignored links
                    continue

                # Only token indexes are added to the set
                parse[PARSE_LINK_SET].add((int(link[0]), int(link[2])))

            line_count += 1

        parses.append(parse)

    return parses


def print_parses(sentences, parses, filename):
    """
        Print parses to file (for sequential and random eval methods)
    """
    print("writing parses file to '{}'".format(filename))
    with open(filename, 'w') as fo:
        for sent, parse in zip(sentences, parses):
            fo.write(" ".join(sent) + "\n")
            # Remove brackets from LG-unparsed words
            for link in parse:
                if link[1][0] == "[" and link[1][-1] == "]":
                    link[1] = link[1][1:-1]
                if link[3][0] == "[" and link[3][-1] == "]":
                    link[3] = link[3][1:-1]
                fo.write(" ".join(link) + "\n")
            fo.write("\n")

    print("Finished writing parses file")


def save_parses(sentence_parses: List[Tuple[str, set, int]], file_name: str, options: int):
    """
        Print parses to file (for sequential and random eval methods)
    """
    print("writing parses file to '{}'".format(file_name))

    with open(file_name, 'w') as fo:
        for sent in sentence_parses:
            print_output(["###LEFT-WALL###"] + (sent[0].strip()).split(), list(sent[1]), options, fo)

    print("Finished writing parses file")


def make_sequential(sentence_parses: List[Tuple[str, set, int]], options: int):
    """
        Make sequential parses (each word simply linked to the next one),
        to be used as baseline
    """
    sequential_parses = []

    no_left_wall = options & BIT_NO_LWALL

    for sp in sentence_parses:
        links  = {(0, 1)}

        for i in range(1, len(sp[0].split())):
            links.add((i, i + 1))

        sequential_parses.append((sp[0].strip(), links, 1 if no_left_wall else 0))

    return sequential_parses


def make_random(sents: List[Tuple[str, set, int]], options: int):
    """
        Make random parses (from LG-parser "any"), to use as baseline
    """
    any_dict = Dictionary('any') # Opens dictionary only once
    po = ParseOptions(min_null_count=0, max_null_count=999)
    po.linkage_limit = 100
    options = 0x00000000 | BIT_STRIP #| BIT_ULL_IN
    options |= BIT_CAPS

    random_parses = []

    for sent in sents:
        num_words = len(sent[0])
        # curr_sent.insert(0, "###LEFT-WALL###")

        # substitute words with numbers, to avoid token-splitting by LG "any"
        fake_words = ["w{}".format(x) for x in range(1, num_words + 1)]
        sent_string = " ".join(fake_words)
        sentence = Sentence(sent_string, any_dict, po)
        linkages = sentence.parse()
        num_parses = len(linkages)                          # check nbr of linkages in sentence

        links = []

        if num_parses > 0:
            idx = random.randint(0, num_parses - 1)         # choose a random linkage index
            linkage = Linkage(idx, sentence, po._obj)       # get the random linkage
            tokens, links = parse_postscript(linkage.postscript().replace("\n", ""), options)

        random_parses.append((sent[0], set(links), 0))

    return random_parses


def eval_parses(test_parses: list, ref_parses: list, options: int, verbose: bool, ofile=sys.stdout) -> ParseQuality:
    """
        Compares test_parses against ref_parses link by link
        counting errors

    :param test_parses:     List of test parses in format, prepared by get_parses.
    :param ref_parses:      List of reference parses.
    :param verbose:         Boolean value which enables intermediate result output if set to True.
    :param ofile:           Output file handle.
    :return:                ParseQuality class instance filled with the result data.
    """

    total_parse_quality = ParseQuality()

    if len(ref_parses) != len(test_parses):
        raise EvalError("Error: files don't contain same parses. "
                        "Number of sentences missmatch. Ref={}, Test={}".format(len(ref_parses), len(test_parses)))

    logger.info("\nTest Set\tReference Set\tIntersection\tRecall\tPrecision\tF1")
    logger.info("-" * 75)

    for ref_parse, test_parse in zip(ref_parses, test_parses):

        if ref_parse[PARSE_SENTENCE] != test_parse[PARSE_SENTENCE]:
            raise EvalError("Error: Something went wrong. Sentences missmatch." +
                            ref_parse[PARSE_SENTENCE] + "\n" + test_parse[PARSE_SENTENCE])

        test_tokens = ["###LEFT-WALL###"] + test_parse[PARSE_SENTENCE].split()
        ref_tokens = ["###LEFT-WALL###"] + ref_parse[PARSE_SENTENCE].split()

        test_set = get_link_set(test_tokens, test_parse[PARSE_LINK_SET], options)
        ref_set = get_link_set(ref_tokens, ref_parse[PARSE_LINK_SET], options)

        pq = parse_quality(test_set, ref_set)

        pq.ignored += test_parse[PARSE_IGNORED]

        logger.info(f"{test_parse[0]}")
        logger.info("{} {} {} {} {} {}".format(test_set, ref_set, test_set & ref_set,
              ParseQuality.recall_str(pq), ParseQuality.precision_str(pq), ParseQuality.f1_str(pq)))

        total_parse_quality += pq

    return total_parse_quality


def compare_ull_files(test_path, ref_path, options: int, **kwargs) -> ParseQuality:
    """
    Initiate evaluation process for one or multiple files.

    :param test_path:       Path to file(s) to be tested.
    :param ref_path:        Path to reference file(s).
    :param options:         Bit mask integer representing options.
    :return:                ParseQuality class instance holding parse quality results for the whole corpus
                            (all files if test_path is a directory name).
    """
    total_parse_quality = ParseQuality()
    total_file_count = 0

    stat_file = f"{kwargs.get('output_path', os.environ['PWD'])}/{os.path.split(test_path)[1]}.stat"

    print(stat_file)

    parser_type = kwargs.get("parser_type", "link-grammar-exe")

    # Dictionary with function reference and argument index tuples
    parsers = {"sequential": (make_sequential, 1), "random": (make_random, 1)}

    # Actual function and argument index
    operation, arg_index = parsers.get(parser_type, (None, None))

    is_multifile = os.path.isdir(test_path)

    def save_parse_quality(pq: ParseQuality, file_path: str) -> None:

        with open(file_path, "w") as ofile:
            # print("File being tested: '" + test_file + "'", file=ofile)
            # print("Reference file   : '" + ref_file + "'\n", file=ofile)
            print(ParseQuality.text(total_parse_quality), file=ofile)

    def evaluate(test_file: str) -> None:
        """
        Evaluation function

        :param test_file:       Path to a test file.
        :return:                None.
        """
        nonlocal total_parse_quality
        nonlocal total_file_count

        file_name = os.path.split(test_file)[1]
        dest_path = kwargs.get("output_path", os.environ["PWD"])
        stat_file = f"{dest_path}/{file_name}.stat"
        ull_file  = f"{dest_path}/{file_name}.ull"

        # 'ref_path' should point to reference file if corpus is a single file,
        # path to reference corpus directory otherwise. In later case name of each reference file must exactly match
        # the name of the corresponding corpus file.
        ref_file = f"{ref_path}/{file_name}" if is_multifile else ref_path

        logger.info("\nComparing parses:")
        logger.info("-----------------")
        logger.info("File being tested: '" + test_file + "'")
        logger.info("Reference file   : '" + ref_file + "'")
        logger.info("Result file      : '" + stat_file + "'")

        try:
            ref_parses = get_parses(load_ull_file(ref_file), options & BIT_NO_LWALL)

            # Load parse file if simple evaluation is expected.
            if operation is None:
                test_parses = get_parses(load_ull_file(test_file), options & BIT_NO_LWALL)

            # Perform parsing and saving if random or sequential parses are expected.
            else:
                test_parses = operation(ref_parses, options)
                save_parses(test_parses, ull_file, options)

            # Here comes parse evaluation
            file_quality = eval_parses(test_parses, ref_parses, options, False)

            if is_multifile and (options & BIT_SEP_STAT):
                save_parse_quality(file_quality, stat_file)

            total_parse_quality += file_quality
            total_file_count += 1

        except IOError as err:
            logger.critical("IOError: " + str(err))

        except Exception as err:
            logger.critical("evaluate(): Exception: " + str(err))
            logger.debug(traceback.print_exc())
            raise

    if not (os.path.isfile(test_path) or os.path.isdir(test_path)):
        raise FileNotFoundError("Path '" + test_path + "' does not exist.")

    if ref_path is None:
        raise ValueError("Reference corpus is not specified")

    output_path = kwargs.get("output_path", os.environ["PWD"])

    # print(f"options = {bin(options)}")

    if not os.path.isdir(output_path):
        raise FileNotFoundError("Path '" + output_path + "' does not exist.")

    # If corpus is a directory with multiple filese
    if os.path.isdir(test_path):
        if not os.path.isdir(ref_path):
            raise ValueError("If 'corpus_path' is a directory 'reference_path' "
                                   "should be an existing directory path too.")

        # Evaluate each file of the corpus and summarize statistics
        traverse_dir_tree(test_path, ".ull", [evaluate, test_path], None, True)

    # If corpus is a single file
    else:
        if not os.path.isfile(ref_path):
            raise ValueError("If 'corpus_path' is a file 'reference_path' should be an "
                                   "existing file path too.")

        # Evaluate a single file
        evaluate(test_path)

    # Save corpus statistics to a file
    save_parse_quality(total_parse_quality, stat_file)

    logger.info("\n" + total_parse_quality.text(total_parse_quality))

    return total_parse_quality
