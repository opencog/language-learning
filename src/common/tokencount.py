import logging
import os
from typing import Dict, List
from subprocess import Popen, PIPE
from .dirhelper import traverse_dir_tree
from .sedcommands import get_sed_cmd_common_part

__all__ = [
    'update_token_counts',
    'count_tokens',
    'load_token_counts',
    'save_token_counts',
    'dump_token_counts',
    'unbox_tokens',
    'TokenCountError'
]


class TokenCountError(Exception):
    pass


def unbox_tokens(tokens: List[str]) -> List[str]:
    """
    Remove square brackets around tokens if any.

    :param tokens:          List of tokens.
    :return:                List of "unboxed" tokens
    """
    return [t[1:-1] if t[0] == "[" and t[-1] == "]" else t for t in tokens]


def update_token_counts(corpus_path: str, token_counts: Dict[str, int], options: int) -> int:
    """
    Update token counts saved in 'token_count' dictionary using the same settings as parser.
        The corpus is filtered by 'sed' according to 'options' bit mask.

    :param corpus_path:     Path to corpus file.
    :param token_counts:    Dictionary of token appearance counts.
    :param options:         Bit mask representing parsing options.
    :return:                Total number of tokens in corpus file.
    """
    sed_cmd = get_sed_cmd_common_part(options) + [corpus_path]

    with Popen(sed_cmd, stdout=PIPE, stderr=PIPE) as proc_sed:

        # Read pipes to get complete output returned by link-parser
        raw_stream, err_stream = proc_sed.communicate()

        # Check return code to make sure the process completed successfully.
        if proc_sed.returncode != 0:
            raise TokenCountError(f"Process '{sed_cmd[0]}' terminated with exit code: {proc_sed.returncode} "
                                  f"and error message:\n'{err_stream.decode()}'")

    total_count = 0

    for line in raw_stream.decode().split("\n"):

        for token in unbox_tokens([t.strip() for t in line.split()]):

            # Increment token count
            token_counts[token] = token_counts.get(token, 0) + 1

            # Count total number of tokens appearances
            total_count += 1

    return total_count


def save_token_counts(token_counts: Dict[str, int], output_path: str) -> None:
    """
    Save token appearance counts into the file.

    :param token_counts:    Dictionary with token appearance counts.
    :param output_path:     Output directory path.
    :return:                None
    """
    logger = logging.getLogger(__name__ + ".save_token_counts")

    if not len(token_counts):
        logger.warning(f"No tokens to save.")

    counts_list = sorted([(key, value) for key, value in zip(token_counts.keys(), token_counts.values())],
                         key=lambda a: a[0])

    with open(output_path, "w") as out_file:
        for entry in counts_list:
            print(entry[0], entry[1], file=out_file)

    logger.warning(f"Token counts are saved in '{output_path}'")


def load_token_counts(file_path: str) -> Dict[str, int]:
    """
    Load token appearance data from the file.

    :param file_path:       Path to file with token appearance data.
    :return:                Dictionary with token appearance counts.
    """
    logger = logging.getLogger(__name__ + ".load_token_counts")

    # Clear dictionary to avoid confusion.
    token_counts = {}

    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        tokens = line.split(" ")

        if len(tokens) > 2:
            raise TokenCountError("Invalid file format. Make sure your specified right file path.")

        token_counts[tokens[0]] = int(tokens[1])

    logger.info(f"Token appearance dictionary has been successfuly populated from '{file_path}'")

    return token_counts


def count_tokens(corpus_path: str, options: int) -> Dict[str, int]:
    """
    Count token appearances in the corpus file taking into account settings specified by 'options'

    :param corpus_path:     Path to corpus file(s).
    :param output_path:     Output directory path.
    :param options:         Option bit mask. The same value as used by parser.
    :return:                Dictionary with token appearances.
    """
    token_counts = {}

    def on_file(file: str, args: list) -> None:
        update_token_counts(file, token_counts, options)

    if not (os.path.isfile(corpus_path) or os.path.isdir(corpus_path)):
        raise FileNotFoundError("Path '" + corpus_path + "' does not exist.")

    # Count token appearances
    if os.path.isdir(corpus_path):
        traverse_dir_tree(corpus_path, "", [on_file], None, True)

    else:
        update_token_counts(corpus_path, token_counts, options)

    return token_counts


def dump_token_counts(corpus_path: str, output_path: str, options: int):
    """
    Count token appearances and save them to a specified destination using output file name convention.

    :param corpus_path:     Path to corpus file(s).
    :param output_path:     Output directory path.
    :param options:         Option bit mask. The same value as used by parser.
    :return:                None
    """
    token_counts = count_tokens(corpus_path, options)

    if not os.path.isdir(output_path):
        raise FileNotFoundError("Path '" + output_path + "' does not exist.")

    output_path += "/" + os.path.split(corpus_path)[1] + ".cnt"

    # Save data to the file
    save_token_counts(token_counts, output_path)
