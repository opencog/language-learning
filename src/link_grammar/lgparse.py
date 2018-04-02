"""
    This module is common for multiple Link Grammar parse scripts. It exports parse_text() function capable of
        parsing text files and calculating parse statistics.
"""
import sys
import re
import os
from linkgrammar import LG_Error, Sentence, ParseOptions, Dictionary

__all__ = ['parse_text', 'BIT_CAPS', 'BIT_RWALL', 'BIT_STRIP', 'BIT_OUTPUT', 'BIT_OUTPUT_DIAGRAM',
           'BIT_OUTPUT_POSTSCRIPT', 'BIT_OUTPUT_CONST_TREE']

__version__ = "1.0.0"

BIT_CAPS  = 0x01        # Keep capitalized letters in tokens
BIT_RWALL = 0x02        # Keep RIGHT-WALL tokens and the links
BIT_STRIP = 0x04        # Strip off token suffixes
BIT_OUTPUT= 0x18        # Output format

# Output format constants. If no bits set ULL defacto format is used
BIT_OUTPUT_DIAGRAM = 0x08
BIT_OUTPUT_POSTSCRIPT = 0x10
BIT_OUTPUT_CONST_TREE = 0x18

def parse_text(dict_path, corpus_path, output_path, linkage_limit, options) \
        -> (float, float, float):
    """
    Link parser invocation routine.

    :param dict_path: name or path to the dictionary
    :param corpus_path: path to the test text file
    :param output_path: output file path
    :param linkage_limit: maximum number of linkages LG may return when parsing a sentence
    :param options: bit field. Use bit mask constants to set or reset one or multiple bits:
                BIT_CAPS  = 0x01    Keep capitalized letters in tokens untouched if set,
                                    make all lowercase otherwise.
                BIT_RWALL = 0x02    Keep all links with RIGHT-WALL if set, ignore them otherwise.
                BIT_STRIP = 0x04    Strip off token suffixes if set, remove them otherwise.
    :return: tuple (float, float, float):
                - percentage of totally parsed sentences;
                - percentage of completely unparsed sentences;
                - percentage of parsed sentences;
    """

    def parse_postscript(text, ofile) -> (int, int, float):
        """
        Parse postscript notation of the linkage.

        :param text: text string returned by Linkage.postscript() method.
        :param ofile: output file object refference
        :return: Tuple (int, int, float):
                    - Number of successfully parsed linkages;
                    - Number of completely unparsed linkages;
                    - Average value of successfully linked tokens.
        """

        def strip_token(token) -> str:
            """
            Strip off suffix substring
            :param token: token string
            :return: stripped token if a suffix found, the same token otherwise
            """
            if token.startswith(".") or token.startswith("["):
                return token

            pos = token.find("[")

            # If "." is not found
            if pos < 0:
                pos = token.find(".")

                # If "[" is not found or token starts with "[" return token as is.
                if pos <= 0:
                    return token

            return token[:pos:]

        def parse_tokens(txt, opt) -> list:
            """
            Parse string of tokens
            :param txt: string token line extracted from postfix notation output string returned by Linkage.postfix()
                    method.
            :param opt: bit mask option value (see parse_test() description for more details)
            :return: list of tokes
            """
            toks = []
            start_pos = 1
            end_pos = txt.find(")")

            while end_pos - start_pos > 0:
                token = txt[start_pos:end_pos:]

                if opt & BIT_STRIP == BIT_STRIP:
                    token = strip_token(token)

                if token.find("-WALL") > 0:
                    token = "###" + token + "###"
                else:
                    if opt & BIT_CAPS == 0:
                        token = token.lower()

                if token.find("RIGHT-WALL") < 0:
                    toks.append(token)
                elif opt & BIT_RWALL == BIT_RWALL:
                    toks.append(token)

                start_pos = end_pos + 2
                end_pos = txt.find(")", start_pos)

            return toks

        def calc_stat(toks) -> (int, int, float):
            """
            Calculate percentage of successfully linked tokens. Token in square brackets considered to be unlinked.

            :param toks: List of tokens.
            :return: Tuple (int, int, float):
                        - 1 if all tokens are linked, 0 otherwise;
                        - 1 if all tokens are unlinked, 1 otherwise;
                        - Percentage of successfully parsed tokens.
            """
            total = len(toks)

            # Nothing to calculate if no tokens found
            if total == 0:
                return 0.0

            # LEFT-WALL is not taken into account
            total -= 1

            # Initialize number of unlinked tokens
            unlinked = 0

            # We assume that all tokens included in square brackets are unlinked
            for token in toks:
                if token.startswith("["):
                    unlinked += 1

            return unlinked == 0, total == unlinked, 1.0 if unlinked == 0 else 1.0 - float(unlinked) / float(total)

        def parse_links(txt, toks) -> list:
            """
            Parse links represented in postfix notation and prints them in OpenCog notation.

            :param txt: link list in postfix notation
            :param toks: list of tokens previously extracted from postfix notated output
            :return: List of links in ULL format
            """
            links = []
            token_count = len(toks)
            start_pos = 1
            end_pos = txt.find("]")

            q = re.compile('(\d+)\s(\d+)\s\d+\s\(.+\)')

            while end_pos - start_pos > 0:
                mm = q.match(txt[start_pos:end_pos:])

                if mm is not None:
                    index1 = int(mm.group(1))
                    index2 = int(mm.group(2))

                    if index2 < token_count:
                        links.append((index1, toks[index1], index2, toks[index2]))

                start_pos = end_pos + 2
                end_pos = txt.find("]", start_pos)

            return links

        def print_output(toks, links, ofl):
            """
            Print links in ULL format to the output specified by 'ofl' variable.

            :param toks: List of tokens.
            :param links: List of links.
            :param ofl: Output file handle.
            :return:
            """
            for token in tokens[1:]:
                ofl.write(token + ' ')

            ofl.write('\n')

            print("Result: " + str(calc_stat(toks)), file=ofl)

            for link in links:
                print(link[0], link[1], link[2], link[3], file=ofl)

            print('', file=ofl)

        # def parse_postscript(text, ofile):
        p = re.compile('\[(\(LEFT-WALL\).+\(RIGHT-WALL\))\]\[(.+)\]\[0\]')
        m = p.match(text)

        if m is not None:
            tokens = parse_tokens(m.group(1), options)
            sorted_links = sorted(parse_links(m.group(2), tokens), key=lambda x: (x[0], x[2]))
            print_output(tokens, sorted_links, ofile)

            return calc_stat(tokens)

        return 0, 0, 0.0

    input_file_handle = None
    output_file_handle = None

    # Sentence statistics variables
    sent_full = 0                   # number of fully parsed sentences
    sent_none = 0                   # number of completely unparsed sentences
    sent_stat = 0.0                 # average value of parsed sentences (linkages)

    line_count = 0                  # number of sentences in the corpus

    try:
        po = ParseOptions(min_null_count=0, max_null_count=999)
        po.linkage_limit = linkage_limit

        di = Dictionary(dict_path)

        input_file_handle = open(corpus_path)
        output_file_handle = sys.stdout if output_path is None else open(output_path, "w")

        for line in input_file_handle:
            sent = Sentence(line, di, po)
            linkages = sent.parse()

            # Number of linkages taken in statistics estimation
            linkage_countdown = 1

            temp_full = 0
            temp_none = 0
            temp_stat = 0.0

            for linkage in linkages:
                # print(linkage.diagram())

                (f, n, s) = parse_postscript(linkage.postscript().replace("\n", ""), output_file_handle)

                if linkage_countdown:
                    temp_full += f
                    temp_none += n
                    temp_stat += s
                    linkage_countdown -= 1

            if len(linkages) > 0:
                sent_full += temp_full
                sent_none += temp_none
                sent_stat += temp_stat / float(len(linkages))
            else:
                sent_none += 1

            line_count += 1

        # Prevent interleaving "Dictionary close" messages
        ParseOptions(verbosity=0)

    except LG_Error as err:
        print(str(err))

    except IOError as err:
        print(str(err))

    except FileNotFoundError as err:
        print(str(err))

    finally:
        if input_file_handle is not None:
            input_file_handle.close()

        if output_file_handle is not None and output_file_handle != sys.stdout:
            output_file_handle.close()

        return (0.0, 0.0, 0.0) if line_count == 0 else (float(sent_full) / float(line_count),
                                                        float(sent_none) / float(line_count),
                                                        sent_stat / float(line_count))


def traverse_dir(root, file_ext, on_file, on_dir=None, is_recursive=False):
    """
    Traverse directory tree and call callback functions for each file and subdirectory.
    :param root: Root directory to start traversing from.
    :param file_ext: File extention to filter files by type.
    :param on_file: callback function pointer to be called each time the file is found.
    :param on_dir: callback function pointer to be called each time the folder is found.
    :param is_recursive: Tells the function to recursively traverse directory tree if set to True, otherwise False.
    :return:
    """
    for entry in os.scandir(root):

        if entry.is_dir():
            if on_dir is not None:
                on_dir(entry.path)

            if is_recursive:
                traverse_dir(entry.path, file_ext, on_file, on_dir, True)

        elif entry.is_file() and (len(file_ext) < 1 or (len(file_ext) and entry.path.endswith(file_ext))):
            if on_file is not None:
                on_file(entry.path)
