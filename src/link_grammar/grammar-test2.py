#!/usr/bin/env python3

import sys
import os
import getopt
from link_grammar.lgparse import *

__version__ = "2.0.2"


def main(argv):
    """
Usage: grammar-test2.py -d <dict_path> -i <input_path> [-o <output_path>] [-s <stat_path>] [OPTIONS]

    dict_path           Path to grammar definition file (or directory with multiple such files) to be tested.
                        The files should be in proper Link Grammar format.
    input_path          Input corpus file or directory path. In case of directory the script will traverse all
                        subdirectories, parse each file in there and calculate overal statistics.
    output_path         Output directory path to store parse text files in. sys.stdout is used if not specified.
    stat_path           Statistics output file path. sys.stdout is used if not specified.

    OPTIONS:
        -h  --help              Print usage info.
        -c  --caps              Leave CAPS untouched.
        -w  --right-wall        Keep RIGHT-WALL tokens.
        -r  --rm-dir            Remove grammar directory if it already exists.
        -n  --no-strip          Do not strip token suffixes.
        -u  --ull-input         ULL links are used as input. This option should be specified to use only sentences
                                    and filter out link lines.
        -l  --linkage-limit     Maximum number of linkages Link Grammar may return when parsing a sentence.
                                Default is one linkage.
        -g  --grammar-dir       Directory path where newly created grammar should be stored.
        -t  --template-dir      LG grammar directory to be used as template when creating new grammars directories.
                                If short name such as 'ru' is used, default route LG path for specified grammar is used.
        -f  --output-format     Parse output format, can be "ull" (default), "diagram", "postscript", "constituent"
    """

    dict_path       = None
    input_path      = None
    output_path     = None
    options         = 0 | BIT_STRIP | BIT_ULL_IN
    linkage_limit   = None
    grammar_path    = None
    template_path   = None
    stat_path       = None

    print("grammar-test2.py ver." + __version__)

    try:
        opts, args = getopt.getopt(argv, "hcwrnud:i:o:l:g:t:f:s:", ["help", "caps", "right-wall", "rm-dir", "no-strip",
                                                            "ull-input", "dictionary=", "input=", "output=",
                                                            "linkage-limit=", "grammar-dir=", "template-dir=",
                                                            "output-format", "stat-path="])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(main.__doc__)
                exit(0)
            elif opt in ("-c", "--caps"):
                options |= BIT_CAPS
            elif opt in ("-w", "--right-wall"):
                options |= BIT_RWALL
            elif opt in ("-r", "--rm-dir"):
                options |= BIT_RM_DIR
            elif opt in ("-n", "--no-strip"):
                options &= (~BIT_STRIP)
            elif opt in ("-u", "--ull-input"):
                options &= (~BIT_ULL_IN)
            elif opt in ("-d", "--dictionary"):
                dict_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-i", "--input"):
                input_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-o", "--output"):
                output_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-l", "--linkage-limit"):
                linkage_limit = int(arg)
            elif opt in ("-g", "--grammar-dir"):
                grammar_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-t", "--template-dir"):
                template_path = arg.replace("~", os.environ['HOME'])
            elif opt in ("-f", "--output-format"):
                if arg == "diagram":
                    options |= BIT_OUTPUT_DIAGRAM
                elif arg == "postscript":
                    options |= BIT_OUTPUT_POSTSCRIPT
                elif arg == "constituent":
                    options |= BIT_OUTPUT_CONST_TREE
            elif opt in ("-s", "--stat-path"):
                stat_path = arg.replace("~", os.environ['HOME'])

    except getopt.GetoptError:
        print(main.__doc__)
        exit(1)

    if input_path is None:
        print("Error: Input file path is not specified.")
        print(main.__doc__)
        exit(1)

    if linkage_limit is None:
        linkage_limit = 1

    if template_path is None:
        template_path = "en"

    if grammar_path is None:
        grammar_path = "/usr/local/share/link-grammar"

    if output_path is None:
        output_path = os.environ['PWD']

    if dict_path is None:
        dict_path = "en"
        # print("Error: Dictionary file/directory path is not specified.")
        # print(main.__doc__)
        # exit(1)

    try:
        parse_corpus_files(input_path, output_path, dict_path, grammar_path, template_path,
                           linkage_limit, options)

    except OSError as err:
        print(str(err))


if __name__ == "__main__":
    main(sys.argv[1:])
