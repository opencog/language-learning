#!/usr/bin/env python3

import sys, re, os, shutil, locale, getopt
from linkgrammar import LG_Error, Linkage, Sentence, ParseOptions, Dictionary, Clinkgrammar as clg

__version__             = "1.3"
DEFAULT_LG_DICT_PATH    = "/usr/local/share/link-grammar"
OUTPUT_DIAGRAM          = 0
OUTPUT_POSTSCRIPT       = 1
OUTPUT_CONSTITUENT      = 2

def main(argv):
    """
        Usage: grammar-test.py [-f <dict_file_path> | -d <dir_with_dict_files>] -g <grammar_dir> -c <corpus_file_path>
                                [-t <template_dict_path> -o <output_format> -r]

                dict_file_path    - grammar file path. Grammar file name should be: 'grammar-name_cluster-info_yyyy-MM-dd_hhhh.4.0.dict'
                                                                                    (e.g. poc-turtle_8C_2018-03-03_0A10.4.0.dict)
                                      where
                                          grammar-name    - the name of the language the grammar file was created for
                                          NC              - N is the number of clusters used while creating the grammar, C is a literal 'C'
                                          yyyy            - year (e.g. 2018)
                                          MM              - month
                                          dd              - day of the month
                                          hhhh            - hexadecimal sequential number

                dir_with_dict_files - path to directory with .dict files

                grammar_dir_path    - grammar root directory, where each language grammar is stored in a separate subdirectory

                corpus_file_path    - path to a test corpus file

                template_dict_path  - path to a grammar subfolder which would be used as a template when creating new grammar subdirectory

                output_format       - output format, can be "diagram" (default), "postscript", "constituent"
    """

    file_path           = None
    lg_dict_path        = None
    template_dict_path  = None
    corpus_path         = None
    server_ip           = None
    output_id           = None

    try:
        opts, args = getopt.getopt(argv, "hf:g:t:c:o:u:", ["help", "file=", "grammar-root=", "template-dir=", "test-corpus=",
                                                           "output-format", "server-url"])

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print_help()
                exit()
            elif opt in ("-f", "--file"):
                file_path = arg
            elif opt in ("-g", "--grammar-root"):
                lg_dict_path = arg
            elif opt in ("-t", "--template-dir"):
                template_dict_path = arg
            elif opt in ("-c", "--test-corpus"):
                corpus_path = arg
            elif opt in ("-o", "--output-format"):
                if arg is None:
                    output_id = OUTPUT_DIAGRAM
                elif arg.lower() == "diagram":
                    output_id = OUTPUT_DIAGRAM
                elif arg.lower() == "postscript":
                    output_id = OUTPUT_POSTSCRIPT
                elif arg.lower() == "constituent":
                    output_id = OUTPUT_CONSTITUENT
                else:
                    output_id = 0
                    print("Warning: Unknown output format '{}'. Default output format is used instead.".format(arg))
            elif opt in ("-u", "--server-url"):
                print("Option '-u' is not implemented in current version of the script.")
                server_ip = arg

    except getopt.GetoptError:
        print_help()
        exit(1)

    if file_path is None:
        print("Error: Dictionary file path is not specified.")
        print_help()
        exit(1)

    if lg_dict_path is None:
        print("Error: Dictionary root path is not specified.")
        print_help()
        exit(1)

    if corpus_path is None:
        print("Error: Test corpus file path is not specified.")
        print_help()
        exit(1)

    # Extract grammar name and a name of the new grammar directory from the file name
    (template_dict_name, dict_path) = get_dir_name(file_path)

    if dict_path is None:
        print("Error: Unable to parse file name.")
        exit(2)

    # If template dictionary path is not specified use default LG dictionary path and language name
    #   extracted from dictionary file name
    if template_dict_path is None:
        template_dict_path = DEFAULT_LG_DICT_PATH + "/" + template_dict_name
        print("Warning: Template dictionary path is not specified. Default path '{}' is used instead.".format(DEFAULT_LG_DICT_PATH))

    dict_path = lg_dict_path + "/" + dict_path

    print(template_dict_path, dict_path, sep="\n")

    try:
        # If the dictionary directory does not exist
        if not os.path.isdir(dict_path):

            # Create dictionary directory using existing one as a template
            shutil.copytree(template_dict_path, dict_path)
            print("Info: Directory '" + dict_path + "' with template files has been created.")

            # Replace dictionary file '4.0.dict' with a new one
            shutil.copy(file_path, dict_path + "/4.0.dict")
            print("Info: Dictionary file has been replaced with '" + dict_path + "'.")
        else:
            print("Info: Directory '" + dict_path + "' already exists.")

        # Run Link Grammar parser
        parse_text(dict_path, corpus_path, output_id)

    except LG_Error as err:
        print(str(err))
        exit(2)

    except IOError as err:
        print(str(err))
        exit(3)

    except FileNotFoundError as err:
        print(str(err))
        exit(4)

    except OSError as err:
        print(str(err))
        exit(5)

#
# Print usage info
#
def print_help():
    print("Grammar test script v." + __version__)
    print(main.__doc__)
#
# Extract the first part of the file name to use it as a name for grammar directory
#
def get_dir_name(file_name):
    p = re.compile('(/?([._\w\d~-]*/)*)(([a-zA-Z-]+)_[0-9]{1,3}C_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9A-F]{4})\.(4\.0\.dict)')
    m = p.match(file_name)

    retval = (None, None) if m is None else (m.group(4), m.group(3))
    return (retval)

#
# Link parser invocation routine
#
def parse_text(dict_path, corpus_path, output_id=OUTPUT_DIAGRAM):
    def s(q):
        return '' if q == 1 else 's'

    def linkage_stat(psent, lang, lkgs, sent_po):
        """
        This function mimics the linkage status report style of link-parser
        """
        random = ' of {} random linkages'. \
            format(clg.sentence_num_linkages_post_processed((psent._obj))) \
            if clg.sentence_num_linkages_found(psent._obj) > sent_po.linkage_limit else ''

        print('`{}: Found {} linkage{} ({}{} had no P.P. violations)`'. \
              format(lang, clg.sentence_num_linkages_found(psent._obj),
                     s(clg.sentence_num_linkages_found(psent._obj)), len(lkgs), random))

    po = ParseOptions(min_null_count=0, max_null_count=999)
    #po.linkage_limit = 3

    dict = Dictionary(dict_path) # open the dictionary only once

    with open(corpus_path) as f:
        for line in f:
            print(line, end="")

            sent = Sentence(line, dict, po)
            linkages = sent.parse()
            linkage_stat(sent, dict_path, linkages, po)

            if output_id == OUTPUT_POSTSCRIPT:
                for linkage in linkages:
                    print(linkage.postscript())
            elif output_id == OUTPUT_CONSTITUENT:
                for linkage in linkages:
                    print(linkage.constituent_tree())
            else:
                for linkage in linkages:
                    print(linkage.diagram())

    # Prevent interleaving "Dictionary close" messages
    po = ParseOptions(verbosity=0)


if __name__ == "__main__":
    main(sys.argv[1:])