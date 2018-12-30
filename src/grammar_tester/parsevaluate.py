import sys
import os
import logging
import traceback
# from decimal import Decimal

from ..common.dirhelper import traverse_dir
from .parsestat import parse_quality
from ..common.parsemetrics import ParseQuality


__all__ = ['load_ull_file', 'get_parses', 'eval_parses', 'compare_ull_files', 'EvalError']


PARSE_SENTENCE = 0
PARSE_LINK_SET = 1
PARSE_IGNORED = 2

logger = logging.getLogger(__name__)


class EvalError(Exception):
    pass


def load_ull_file(filename):
    """
        Loads a data file
    """
    with open(filename, "r", encoding="utf-8-sig") as file:
        data = file.read()

    return data


def get_parses(data, ignore_wall: bool=True, sort_parses: bool=True):
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
    parses = []

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

                assert len(link) == 4, "The line appears not to be a link: '{}'".format(line)

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


def eval_parses(test_parses: list, ref_parses: list, verbose: bool, ofile=sys.stdout) -> ParseQuality:
    """
        Compares test_parses against ref_parses link by link
        counting errors

    :param test_parses: List of test parses in format, prepared by get_parses.
    :param ref_parses: List of reference parses.
    :param verbose: Boolean value which enables intermediate result output if set to True.
    :param ofile: Output file handle.
    :return: ParseQuality class instance filled with the result data.
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

        pq = parse_quality(test_parse[PARSE_LINK_SET], ref_parse[PARSE_LINK_SET])

        pq.ignored += test_parse[PARSE_IGNORED]
        pq.sentences += 1

        logger.info("{} {} {} {} {} {}".format(test_parse[PARSE_LINK_SET], ref_parse[PARSE_LINK_SET],
              test_parse[PARSE_LINK_SET] & ref_parse[PARSE_LINK_SET],
              ParseQuality.recall_str(pq), ParseQuality.precision_str(pq), ParseQuality.f1_str(pq)))

        total_parse_quality += pq

    if ofile != sys.stdout or (ofile == sys.stdout and verbose):
        print(ParseQuality.text(total_parse_quality), file=ofile)

    return total_parse_quality


def compare_ull_files(test_path, ref_file, verbose, ignore_left_wall) -> ParseQuality:
    """
    Initiate evaluation process for one or multiple files.

    :param test_path: Path to file(s) to be tested.
    :param ref_file: Path to reference file(s).
    :param verbose: Boolean value which eables intermediate result output if set to True.
    :param ignore_left_wall: Boolean value which tells the script to ignore LEFT-WALL and period links if set to True.
    :return: ParseQuality class instance holding parse quality results for the whole corpus (all files if test_path is
                a directory name).
    """
    total_parse_quality = ParseQuality()
    total_file_count = 0

    def evaluate(test_file):
        """ Callback evaluation function """

        nonlocal total_parse_quality
        nonlocal total_file_count

        out_file = test_file + ".stat"

        if verbose:
            logger.info("\nComparing parses:")
            logger.info("-----------------")
            logger.info("File being tested: '" + test_file + "'")
            logger.info("Reference file   : '" + ref_file + "'")
            logger.info("Result file      : '" + out_file + "'")

        mode = "a" if os.path.isfile(out_file) else "w"

        try:
            ref_data = load_ull_file(ref_file)
            ref_parses = get_parses(ref_data, ignore_left_wall, False)

            test_data = load_ull_file(test_file)
            test_parses = get_parses(test_data, ignore_left_wall, False)

            with open(out_file, mode) as ofile:
                print("File being tested: '" + test_file + "'", file=ofile)
                print("Reference file   : '" + ref_file + "'\n", file=ofile)

                total_parse_quality += eval_parses(test_parses, ref_parses, verbose, ofile)
                total_file_count += 1

        except IOError as err:
            logger.critical("IOError: " + str(err))

        except Exception as err:
            logger.critical("evaluate(): Exception: " + str(err))
            logger.debug(traceback.print_exc())
            raise
    try:
        # If specified name is a file.
        if os.path.isfile(test_path):
            evaluate(test_path)

        # If specified name is a directory.
        elif os.path.isdir(test_path):
            traverse_dir(test_path, ".ull", evaluate, None, True)

        # If file or directory does not exist.
        else:
            raise("Error: File or directory '" + test_path + "' does not exist.")

        logger.info("\n" + total_parse_quality.text(total_parse_quality))

    except IOError as err:
        logger.critical("IOError: " + str(err))
        logger.debug(traceback.print_exc())

    except KeyboardInterrupt:
        logger.warning("Ctrl+C triggered.")

    except Exception as err:
        logger.critical("Exception: " + str(err))
        logger.debug(traceback.print_exc())

    return total_parse_quality
