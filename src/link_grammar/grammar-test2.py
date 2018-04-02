#!/usr/bin/env python3

import sys
import os
import getopt
from link_grammar.lgparse import *

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
        -f  --output-format     Parse output format, can be "ull" (default), "diagram", "postscript", "constituent"
    """

    input_path      = None
    output_path     = None
    options         = 0 | BIT_STRIP
    linkage_limit   = None
    grammar_path    = None

    print("lgparser.py v." + __version__)

    try:
        opts, args = getopt.getopt(argv, "hcrni:o:l:g:", ["help", "caps", "right-wall", "no-strip",
                                                        "input=", "output=", "linkage-limit=", "grammar-dir="])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(main.__doc__)
                exit(0)
            elif opt in ("-c", "--caps"):
                options |= BIT_CAPS
            elif opt in ("-r", "--right-wall"):
                options |= BIT_RWALL
            elif opt in ("-n", "--no-strip"):
                options &= (~BIT_STRIP)
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
              parse_text(grammar_path, input_path, output_path, linkage_limit, options)))

    except OSError as err:
        print(str(err))


if __name__ == "__main__":
    main(sys.argv[1:])
