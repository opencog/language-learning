#!/usr/bin/env python3

import sys
import re
import os
import getopt
from linkgrammar import LG_Error, Sentence, ParseOptions, Dictionary

__version__ = "2.0.1"


def main(argv):
    """
Usage: grammar-test2.py -i <input_path> [-o <output_path>] [OPTIONS]

    input_path          input corpus file path
    output_path         output file path (default is stdout)

    OPTIONS:
        -h  --help              Print usage info.
        -c  --caps              Leave CAPS untouched.
        -r  --right-wall        Keep RIGHT-WALL tokens.
        -n  --no-strip          Do not strip token suffixes.
        -l  --linkage-limit     Maximum number of linkages Link Grammar may return when parsing a sentence.
                                Default is one linkage.
        -g  --grammar-dir       Language short name (e.g. 'ru' for Russian) or path to grammar dictionary directory.
        -t  --template-dir      LG grammar directory to be used as template when creating new grammars directories.
                                If short name such as 'ru' is used, default route LG path for specified grammar is used.

    """

    input_path      = None
    output_path     = None
    is_caps         = False
    is_rwall        = False
    is_strip        = True
    linkage_limit   = None
    grammar_path    = None

    # parse_postscript("[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)][[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]")
    # exit(0)

    print("lgparser.py v." + __version__)

    try:
        opts, args = getopt.getopt(argv, "hcrni:o:l:g:", ["help", "caps", "right-wall", "no-strip",
                                                        "input=", "output=", "linkage-limit=", "grammar-dir="])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(main.__doc__)
                exit(0)
            elif opt in ("-c", "--caps"):
                is_caps = True
            elif opt in ("-r", "--right-wall"):
                is_rwall = True
            elif opt in ("-n", "--no-strip"):
                is_strip = False
            elif opt in ("-i", "--input"):
                input_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-o", "--output"):
                output_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-l", "--linkage-limit"):
                linkage_limit = int(arg)
            elif opt in ("-g", "--grammar-dir"):
                grammar_path = arg

    except getopt.GetoptError:
        print(main.__doc__)
        exit(1)

    if input_path is None:
        print("Error: Input file path is not specified.")
        print(main.__doc__)
        exit(1)

    if linkage_limit is None:
        linkage_limit = 1

    if grammar_path is None:
        grammar_path = "en"

    try:
        print("Total statistics\n-----------------\nCompletely parsed ratio: {0[0]}\n"
              "Completely unparsed ratio: {0[1]}\nAverage parsed ratio: {0[2]}".format(
              parse_text(grammar_path, input_path, output_path, is_caps, is_rwall, is_strip, linkage_limit)))

    except OSError as err:
        print(str(err))


def parse_text(dict_path, corpus_path, output_path, is_caps, is_rwall, is_strip, linkage_limit) \
        -> (float, float, float):
    """
    Link parser invocation routine

    :param dict_path: name or path to the dictionary
    :param corpus_path: path to the test text file
    :param output_path: output file path
    :param is_caps: boolean value tells to leave CAPS in tokens if set to True, make all lowercase otherwise
    :param is_rwall: boolean value tells to leave RIGHT-WALL tokens if set to True, remove otherwise
    :param is_strip: boolean value tells to strip off token suffixes if set to True, remove otherwise
    :param linkage_limit: maximum number of linkages LG may return when parsing a sentence
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

        def parse_tokens(text, caps=False, rw=False, strip=True) -> list:
            """
            Parse string of tokens
            :param text: string token line extracted from postfix notation output string returned by Linkage.postfix()
                    method.
            :param caps: boolean value indicating weather or not CAPS should be untouched or lowercased
            :param rw: boolean value indicating weather or not RIGHT-WALL should be taken into account or ignored
            :param strip: boolean value indicating weather or not token suffixes should be stripped off or left
                    untouched
            :return: list of tokes
            """
            tokens = []
            start_pos = 1
            end_pos = text.find(")")

            while end_pos - start_pos > 0:
                token = text[start_pos:end_pos:]

                if strip:
                    token = strip_token(token)

                if token.find("-WALL") > 0:
                    token = "###" + token + "###"
                else:
                    if not caps:
                        token = token.lower()

                if token.find("RIGHT-WALL") < 0:
                    tokens.append(token)
                elif rw:
                    tokens.append(token)

                start_pos = end_pos + 2
                end_pos = text.find(")", start_pos)

            return tokens

        def calc_stat(tokens) -> (int, int, float):
            """
            Calculate percentage of successfully linked tokens. Token in square brackets considered to be unlinked.

            :param tokens: List of tokens.
            :return: Tuple (int, int, float):
                        - 1 if all tokens are linked, 0 otherwise;
                        - 1 if all tokens are unlinked, 1 otherwise;
                        - Percentage of successfully parsed tokens.
            """
            total = len(tokens)

            # Nothing to calculate if no tokens found
            if total == 0:
                return 0.0

            # LEFT-WALL is not taken into account
            total -= 1

            # Initialize number of unlinked tokens
            unlinked = 0

            # We assume that all tokens included in square brackets are unlinked
            for token in tokens:
                if token.startswith("["):
                    unlinked += 1

            return (unlinked==0, total==unlinked, 1.0 if unlinked == 0 else 1.0 - float(unlinked) / float(total))

        def parse_links(text, tokens) -> list:
            """
            Parse links represented in postfix notation and prints them in OpenCog notation.

            :param text: link list in postfix notation
            :param tokens: list of tokens previously extracted from postfix notated output
            :return:
            """
            links = []
            token_count = len(tokens)
            start_pos = 1
            end_pos = text.find("]")

            p = re.compile('(\d+)\s(\d+)\s\d+\s\(.+\)')

            while end_pos - start_pos > 0:
                m = p.match(text[start_pos:end_pos:])

                if m is not None:
                    index1 = int(m.group(1))
                    index2 = int(m.group(2))

                    if index2 < token_count:
                        links.append((index1, tokens[index1], index2, tokens[index2]))

                start_pos = end_pos + 2
                end_pos = text.find("]", start_pos)

            return links

        def print_output(tokens, links, ofile):

            for token in tokens[1:]:
                ofile.write(token + ' ')

            ofile.write('\n')

            print("Result: " + str(calc_stat(tokens)), file=ofile)

            for link in links:
                print(link[0], link[1], link[2], link[3], file=ofile)

            print('', file=ofile)


        # def parse_postscript(text, ofile):

        p = re.compile('\[(\(LEFT-WALL\).+\(RIGHT-WALL\))\]\[(.+)\]\[0\]')
        m = p.match(text)

        if m is not None:
            tokens = parse_tokens(m.group(1))
            sorted_links = sorted(parse_links(m.group(2), tokens), key=lambda x: (x[0], x[2]))
            print_output(tokens, sorted_links, ofile)

            return calc_stat(tokens)

        return (0, 0, 0.0)


    input_file_handle = None
    output_file_handle = None

    # Sentence statistics variables
    sent_full = 0                   # number of fully parsed sentences
    sent_none = 0                   # number of completely unparsed sentences
    sent_stat = 0.0                 # averege value of parsed sentences (linkages)

    # Number of sentences in the corpus
    line_count = 0

    try:
        po = ParseOptions(min_null_count=0, max_null_count=999)
        po.linkage_limit = linkage_limit

        di = Dictionary(dict_path)

        input_file_handle = open(corpus_path)
        output_file_handle = sys.stdout if output_path is None else open(output_path, "w")

        for line in input_file_handle:
            sent = Sentence(line, di, po)
            linkages = sent.parse()

            # print("Linkages:", len(linkages))

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
        po = ParseOptions(verbosity=0)

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


if __name__ == "__main__":
    main(sys.argv[1:])
