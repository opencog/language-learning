import os
from typing import Optional
from subprocess import PIPE, Popen
from .sedcommands import *
from .dirhelper import traverse_dir_tree


__all__ = [
    'SentCountError',
    'get_sentence_count',
    'get_corpus_sentence_count'
]


class SentCountError(Exception):
    pass


def get_sentence_count(corpus_path: str, options: int) -> int:
    """
    Count sentences in a single corpus file

    :param corpus_path:     Path to a single corpus file.
    :param options:         Bit mask representing parsing options.
    :return:                Number of sentences.
    """
    sentence_count = 0

    sed_cmd = get_sed_cmd_common_part(options) + [corpus_path]

    try:
        # Get number of sentences in input file
        with Popen(sed_cmd, stdout=PIPE) as proc_sed, \
             Popen(["wc", "-l"], stdin=proc_sed.stdout, stdout=PIPE, stderr=PIPE) as proc_wcl:

            # Closing grep output stream will terminate it's process.
            proc_sed.stdout.close()

            # Read pipes to get complete output returned by link-parser
            raw, err = proc_wcl.communicate()

            # Check return code to make sure the process completed successfully.
            if proc_wcl.returncode != 0:
                raise SentCountError("Process '{0}' terminated with exit code: {1} "
                                     "and error message:\n'{2}'.".format("wc", proc_wcl.returncode, err.decode()))

            sentence_count = int((raw.decode("utf-8-sig")).strip())

    except KeyboardInterrupt:
        print("get_sentence_count(): Ctrl+C triggered.")
        raise

    return sentence_count


def get_corpus_sentence_count(corpus_path: str, options: int) -> int:
    """
    Count total number of sentences across all corpus files

    :param corpus_path:     Path to a single corpus file or to a directory with multiple files.
    :param options:         Bit mask holding parse options.
    :return:                Total number of sentences in the corpus.
    """
    total_sentences = 0

    def on_sentence_count(file: str, args: Optional[list]) -> None:
        nonlocal total_sentences
        total_sentences += get_sentence_count(file, options)

    if os.path.isdir(corpus_path):
        traverse_dir_tree(corpus_path, "", [on_sentence_count], None, True)

    else:
        total_sentences = get_sentence_count(corpus_path, options)

    return total_sentences
