import re
import logging
from ..common.optconst import *
from .lgmisc import LGParseError
from typing import List, Optional, Union, Tuple
from decimal import Decimal

"""
    Utilities for parsing postscript notated tokens and links, returned by Link Grammar API method Linkage.postscript()
     
"""

__all__ = ['strip_token', 'parse_tokens', 'parse_links', 'parse_postscript', 'skip_lines', 'trim_garbage',
           'get_link_set', 'prepare_tokens', 'skip_command_response', 'skip_linkage_header', 'split_ps_parses',
           'get_sentence_text', 'get_linkage_cost', 'PS_TIMEOUT_EXPIRED', 'PS_PANIC_DETECTED']

__version__ = "1.0.0"


def strip_token(token) -> str:
    """
    Strip off suffix substring

    :param token:       token string
    :return:            stripped token if a suffix found, the same token otherwise
    """
    if token.startswith("["):
        return token

    pos = token.find("[")

    # If "[" is not found
    if pos < 0:
        pos = token.find(".", 0 if token[0] != "." else 1)

        # If "." is not found return token as is.
        if pos <= 0:
            return token

    return token[:pos:]


def find_end_of_token(text, start_pos: int) -> int:

    # Assume the open brace is already skipped
    braces = 1
    brackets = 0

    pos = start_pos
    text_len = len(text)

    while pos < text_len:

        current = text[pos]

        if current == r")":
            # if not "[)]"
            if not brackets:
                # If not "())"
                if pos + 1 >= text_len or text[pos + 1] != r")":
                    braces -= 1

            if not braces:
                return pos

        elif current == r"[":
            # If not "([)"
            if pos + 1 >= text_len or text[pos + 1] != r")":
                brackets += 1

        elif current == r"]" and brackets:
            brackets -= 1

        pos += 1

    return pos


def parse_tokens(txt, opt) -> (list, int):
    """
    Parse string of tokens, taken from postscript notated LG parse output.
    After several iterations it became obvious that all tokens should be kept in the original list in order to
    avoid issues with links. All filtering necessary for ULL output is now done in print_output(). All filtering
    necessary for parseability statistics estimation is done in prepare_tokens().

    :param txt:         String token line extracted from postfix notation output string returned by Linkage.postfix()
                        method.
    :param opt:         Bit mask option value (see parse_test() description for more details).
    :return:            List of tokens.
    """
    tokens = []
    offset = 0

    # Skip the open brace
    start_pos = 1

    end_pos = txt.find(")(")

    if end_pos < 0:
        end_pos = len(txt)-1

    while end_pos - start_pos > 0:
        token = txt[start_pos:end_pos:]

        # Strip LG suffixes if the option is set.
        if opt & BIT_STRIP == BIT_STRIP:
            token = strip_token(token)

        # All walls are supplied with leading and trailing hashes as agreed for the project.
        if token.find("-WALL") > 0:

            if token in ["RIGHT-WALL", "LEFT-WALL"]:
                tokens.append(r"###" + token + r"###")

            elif token in ["[RIGHT-WALL]", "[LEFT-WALL]"]:
                tokens.append(r"###" + token[1:-1] + r"###")

        else:
            # Even if LEFT-WALL is not defined in .dict file it is still added into the token list
            #   in order for token numbering to be started from one as agreed for ULL project.
            if start_pos == 1:
                tokens.append(r"###LEFT-WALL###")
                offset = 1

            # By default all tokens are kept lower case.
            if opt & BIT_CAPS == 0:
                token = token.lower()

            tokens.append(token)

        start_pos = end_pos + 2
        end_pos = txt.find(")(", start_pos + 1)

        if end_pos < 0:
            end_pos = len(txt)-1

    return tokens, offset


def prepare_tokens(tokens: list, options: int) -> list:
    """
    Prepare (filter) list of tokens according to the options flags for statistics calculation.

    :param tokens:      Initial list of tokens obtained from parse_tokens().
    :param options:     Bit flags.
    :return:            Filtered list of tokens.
    """
    token_count = len(tokens)
    first_token = 0
    last_token = token_count - 1

    if not token_count:
        return tokens

    if options & BIT_NO_LWALL:
        if tokens[0].startswith(r"###") or tokens[0].startswith(r"[##"):
            first_token += 1

        # RIGHT-WALL is not needed if LEFT-WALL is stripped off
        if tokens[last_token].startswith(r"###") or tokens[last_token].startswith(r"[##"):
            last_token -= 1

    if not (options & BIT_RWALL) and (tokens[last_token].startswith(r"###") or tokens[last_token].startswith(r"[##")):
        last_token -= 1

    if options & BIT_NO_PERIOD:
        rw = tokens[last_token] if tokens[last_token].startswith(r"###") or tokens[last_token].startswith(r"[##") \
                                else None

        # Skip RIGHT-WALL if any
        if last_token and tokens[last_token] in [r"###RIGHT-WALL###", r"[###RIGHT-WALL###]"]:
            last_token -= 1

        # Skip period or period in brackets if any
        if last_token and tokens[last_token] in [r"[.]", r"."]:
            last_token -= 1

        # If both period and RIGHT-WALL were found
        if rw is not None:
            # RIGHT-WALL is added to the new list
            return tokens[first_token:last_token+1] + [rw]

    return tokens[first_token:last_token+1]


def parse_links(txt: str, tokens: list, offset: int) -> list:
    """
    Parse links represented in postfix notation and return them as a list of tuples.

    :param txt:         Link list in postfix notation, obtained either from LG API or from link-parser postfix output.
    :param tokens:      List of tokens previously extracted from postfix notated output.
    :param offset:      Token index offset. Equals to 1 if tested grammar has no LEFT-WALL and the former was added
                        during postscript parsing. Offset is necessary for the links to have their indexes properly
                        updated.
    :return:            List of tuples representing token to token links.
    """
    links = []

    token_count = len(tokens)

    start_pos = 1
    end_pos = txt.find("]")

    q = re.compile('(\d+)\s(\d+)\s\d+\s\(.+\)')

    while end_pos - start_pos > 0:
        mm = q.match(txt[start_pos:end_pos:])

        if mm is not None:
            index1, index2 = int(mm.group(1))+offset, int(mm.group(2))+offset

            if index2 < token_count:
                links.append((index1, index2))

        start_pos = end_pos + 2
        end_pos = txt.find("]", start_pos)

    return links


def parse_postscript(text: str, options: int) -> ([], []):
    """
    Parse postscript notation of the linkage.

    :param text:        Text string returned by Linkage.postscript() method.
    :param options      Bit mask, representing different parsing options. See `optconst.py` for details.
    :return:            Tuple of two lists: (tokens, links).
    """
    p = re.compile('\[(\(.+?\)+?)\]\[(.*?)\]\[0\]', re.S)

    m = p.match(text.replace("\n", ""))

    if m is not None:
        tokens, offset = parse_tokens(m.group(1), options)
        links = parse_links(m.group(2), tokens, offset)

        return tokens, links

    raise LGParseError(f"parse_postscript(): regex does not match for:\n{text}")


def get_link_set(tokens: list, links: Union[list, set], options: int) -> set:
    """
    Create link set from link list filtering out unnecessary links according to options bit flags.

    :param tokens:      Token list.
    :param links:       Link list.
    :param options:     Integer bit mask variable.
    :return:            Filtered set of links.
    """
    all_link_set = set(links) if isinstance(links, list) else links
    exc_link_set = set()

    token_count = len(tokens)

    if token_count:
        last_token = token_count - 1

        if options & BIT_NO_LWALL and tokens[0].find("WALL") > -1:
            exc_link_set |= set({(0, i) for i in range(1, token_count)})

            if tokens[last_token].startswith(r"###"):
                exc_link_set |= set({(i, last_token) for i in range(token_count)})

        if options & BIT_NO_PERIOD:
            if tokens[last_token].startswith(r"###"):
                last_token -= 1

            if tokens[last_token] == ".":
                exc_link_set |= set({(i, last_token) for i in range(token_count)})

        if len(exc_link_set):
            return all_link_set - exc_link_set

    return all_link_set


def skip_lines(text: str, lines_to_skip: int) -> int:
    """
     Skip specified number of lines from the beginning of a text string.

    :param text:            Text string with zero or many '\n' in.
    :param lines_to_skip:   Number of lines to skip.
    :return:                Return position of the first character after the specified number of lines is skipped.
    """
    l = len(text)

    pos = 0
    cnt = lines_to_skip

    while l and cnt:
        if text[pos] == "\n":
            cnt -= 1
        pos += 1
    return pos


def skip_command_response(text: str) -> int:
    """
     Skip specified number of lines from the beginning of a text string.

    :param text:        Text string with zero or many '\n' in.
    :return:            Return position of the first character after the command response is skipped.
    """
    l = len(text)

    pos, old = 0, 0

    while l:
        if text[pos] == "\n":
            line = text[old:pos]

            if len(line) and not (line.startswith("Debug:") or line.find(" set to ") >= 0):
                return old

            old = pos + 1 if pos + 1 < l else pos
        pos += 1

    return pos


def trim_garbage(text: str) -> int:
    """
    Strip all characters from the end of string until ']' is reached.

    :param text:    Text string.
    :return:        Return position of a character following ']' or zero in case of a null string.
    """
    l = len(text) - 1

    while l:
        if text[l] == "]":
            return l+1
        l -= 1

    pos = text.rfind("Bye.")

    if pos > 0:
        return pos

    l = len(text) - 1

    while text[l] == " " or text[l] == "\n":
        l -= 1

    return l

PS_TIMEOUT_EXPIRED    = BIT_EXCLUDE_TIMEOUTED
PS_PANIC_DETECTED     = BIT_EXCLUDE_PANICED
PS_EXPLOSION_DETECTED = BIT_EXCLUDE_EXPLOSION


def skip_linkage_header(text: str) -> (int, int):
    """
     Skip linkage text header while checking timiouts and panic mode.

    :param text:            Text string with zero or many '\n' in.
    :return:                Return tuple:
                                - position of the first character of postscript notated link-parser output
                                - error bit mask.
    """
    l = len(text)

    pos, old, err = 0, 0, 0

    while pos < l:
        if text[pos] == "\n":
            line = text[old:pos]

            # Check if the line is not empty
            if len(line):

                # Return starting position if postscript is detected (first character is '[')
                if line.startswith("[("):
                    return old, err

                if line.find("Timer is expired!") >= 0:
                    err |= PS_TIMEOUT_EXPIRED

                if line.find('Entering "panic" mode...') >= 0:
                    err |= PS_PANIC_DETECTED

            old = pos + 1 if pos + 1 < l else pos

        pos += 1

    return -1, err


def split_ps_parses(text: str) -> List[str]:
    """
    Split postscript parses if they are merged together because of the combinatorial explosion of
        first N-1 sentenses, where N is the number of merged sentences.

    :param text:    Postscript notated string variable.
    :return:        List of splitted postscript parses.
    """
    text = text.strip("\n")
    pattern = re.compile(r"^Found\s\d+\slinkages\s\(0\sof.+$|^Panic timer is expired!(?:\n|\r\n?)+(?!Found \d+)", re.M)
    parses = re.split(pattern, text)

    return parses[:-1] if parses[-1] == "" else parses


def get_sentence_text(text: str) -> Optional[str]:
    """
    Retrieve echoed sentence from postscript notated parse string.

    :param text:    Postscript notated string variable.
    :return:        Echoed sentence.
    """
    pos = text.find("No complete linkages found.")

    if pos > 0:
        return text[:pos].replace("\n", "")

    pattern = re.compile(r"^Found \d+ linkages?.+$", re.M)
    match = pattern.search(text)

    if match:
        return text[:match.start()].replace("\n", "")

    logging.getLogger(__name__ + ".get_sentence_text").debug(f"Unable to find echoed sentence in postscript "
                                                             f"parse:\n{text}")

    return None


def get_linkage_cost(text: str):  # -> Optional[int, Tuple[int, str, int]]:
    """
    Retrieve linkage number and cost vector

    :param text:    Linkage text block.
    :return:        A tuple of linkage number and cost vector (UNUSED, DIS, LEN)
    """
    pattern = re.compile(r"^\s*(?:L|Unique l){1}inkage (\d+), cost vector = \(UNUSED=(\d+) DIS=\s*([-+.0-9]+) LEN=(\d+)\)$", re.M)
    data = pattern.findall(text)

    if data is None or len(data) < 1:
        return None

    # if len(data) > 1:
    #     raise LGParseError(f"Found more than one linkage in: {text}")

    return int(data[0][0]), (int(data[0][1]), Decimal(data[0][2]), int(data[0][3]))
