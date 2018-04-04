"""
    This module is common for multiple Link Grammar parse scripts. 
        It exports:
            parse_text()            - function capable of parsing text files and calculating parse statistics.
            parse_corpus_files()    - function capable of traversing directory tree parsing each file.
"""
import sys
import re
import os
import shutil
from linkgrammar import LG_Error, Sentence, ParseOptions, Dictionary

__all__ = ['parse_corpus_files', 'parse_text', 'BIT_CAPS', 'BIT_RWALL', 'BIT_STRIP', 'BIT_OUTPUT',
           'BIT_ULL_IN', 'BIT_RM_DIR', 'BIT_OUTPUT_DIAGRAM', 'BIT_OUTPUT_POSTSCRIPT', 'BIT_OUTPUT_CONST_TREE']

__version__ = "2.0.0"

LG_DICT_PATH = "/usr/local/share"

BIT_CAPS  = 0x01        # Keep capitalized letters in tokens
BIT_RWALL = 0x02        # Keep RIGHT-WALL tokens and the links
BIT_STRIP = 0x04        # Strip off token suffixes
BIT_OUTPUT= 0x18        # Output format
BIT_ULL_IN= 0x20        # If set parse_text() is informed that ULL parses are used as input, so only
                        #   sentences should be parsed, links should be filtered out.
BIT_RM_DIR= 0x40        # Remove grammar dictionary if it already exists. Then recreate it from scratch.

# Output format constants. If no bits set ULL defacto format is used.
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
        link_line = re.compile(r"[ ]*[0-9]+.+", re.S)

        po = ParseOptions(min_null_count=0, max_null_count=999)
        po.linkage_limit = linkage_limit

        di = Dictionary(dict_path)

        input_file_handle = open(corpus_path)
        output_file_handle = sys.stdout if output_path is None else open(output_path, "w")

        for line in input_file_handle:

            # Filter out links when ULL parses are used as input
            if options & BIT_ULL_IN > 0 and link_line.match(line):
                continue

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


def get_dir_name(file_name) -> (str, str):
    """
    get_dir_name - extract template grammar directory name and a name for a new grammar directory

    :param file_name: grammar file name having well defined name notation
    :return: tuple (template_grammar_directory_name, grammar_directory_name)
    """
    p = re.compile(
        '(/?([._\w\d~-]*/)*)(([a-zA-Z-]+)_[0-9]{1,3}C_[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9A-F]{4})\.(4\.0\.dict)')
    m = p.match(file_name)

    return (None, None) if m is None else (m.group(4), m.group(3))


def create_grammar_dir(dict_file_path, grammar_path, template_path, options) -> str:
    """
    Create grammar directory using specified .dict file and other files from template directory.

    :param dict_file_path: Path to .dict file.
    :param grammar_path: Path to a directory where newly created grammar should be stored.
    :param template_path: Path to template directory or language name installed with LG.
    :param options: Bit field that specifies multiple parsing options.
    :return: Path to newly created grammar directory.
    """

    # Extract grammar name and a name of the new grammar directory from the file name
    (template_dict_name, dict_path) = get_dir_name(dict_file_path)

    # print(template_dict_name, dict_path, sep='\n')

    if dict_path is None:
        print("Error: Dictionary file name is expected to have proper notation.")
        return ""

    dict_path = grammar_path + "/" + dict_path

    print(dict_path)

    # If template_dir is not specified
    if template_path is None:
        template_path = LG_DICT_PATH + "/" + template_dict_name

    # If template_dir is simply a language name such as 'en'
    elif template_path.find("/") == -1:
        template_path = LG_DICT_PATH + "/" + template_path

    # Raise exception if template_path does not exist
    if not os.path.isdir(template_path):
        raise FileNotFoundError("Directory '{0}' does not exist.".format(template_path))

    # print(template_path)

    try:
        if os.path.isdir(dict_path):
            print("Info: Directory '" + dict_path + "' already exists.")

            if options & BIT_RM_DIR > 0:
                shutil.rmtree(dict_path, True)
                print("Info: Directory '" + dict_path + "' has been removed. Option '-r' was specified.")

        if not os.path.isdir(dict_path):
            # Create dictionary directory using existing one as a template
            shutil.copytree(template_path, dict_path)
            print("Info: Directory '" + dict_path + "' with template files has been created.")

            # Replace dictionary file '4.0.dict' with a new one
            shutil.copy(dict_file_path, dict_path + "/4.0.dict")
            print("Info: Dictionary file has been replaced with '" + dict_path + "'.")

    except IOError as err:
        print("IOError: " + str(err))

    except FileNotFoundError as err:
        print("FileNotFoundError: " + str(err))

    except OSError as err:
        print("OSError: " + str(err))

    finally:
        return dict_path


def parse_corpus_files(src_dir, dst_dir, dict_dir, grammar_dir, template_dir, linkage_limit, options):
    """
    Traverse corpus folder parsing each file in that folder and subfolders. The function recreates source directory
        structure within the destination one and stores parsing results in newly created directory structure.
    :param src_dir: Source directory with corpus files.
    :param dst_dir: Destination directory to store parsing result files.
    :param dict_dir: Path to dictionary directory or file
    :param grammar_dir: Root directory path to store newly created grammar.
    :param template_dir: Path to template dictionary directory
    :param linkage_limit: Maximum number of linkages. Parammeter for LG API.
    :param options: Parse options bit field.
    :return:
    """
    def on_dict_file(path):
        """
        Callback function envoked for every .dict file specified

        :param path: Path to .dict file
        :return:
        """
        new_grammar_path = ""

        file_count = 0
        full_ratio = 0.0
        none_ratio = 0.0
        avrg_ratio = 0.0

        def recreate_struct(dir_path):
            """
            Callback function that recreates directory structure of the source folder
            within the destination one
            """
            new_path = dst_dir + "/" + dir_path[len(src_dir) + 1:]

            try:
                # If the subdirectory does not exist in destination root create it.
                if not os.path.isdir(new_path):
                    print(new_path)
                    os.mkdir(new_path)

            except OSError as err:
                print("Error: " + str(err))

        def on_corpus_file(file_path):
            # print(file_path)

            p, f = os.path.split(file_path)
            # print(os.path.join(dst_dir, f))
            # print(new_grammar_path)

            f_ratio = 0.0
            n_ratio = 0.0
            a_ratio = 0.0

            try:
                f_ratio, n_ratio, a_ratio = parse_text(new_grammar_path, file_path, os.path.join(dst_dir, f),
                                                    linkage_limit, options)

                file_count += 1
                full_ratio += f_ratio
                none_ratio += n_ratio
                avrg_ratio += a_ratio

            except OSError as err:
                print(str(err))

        # =============================================================================
        # def on_dict_file(path):
        # =============================================================================
        new_grammar_path = create_grammar_dir(path, grammar_dir, template_dir, options)

        if len(new_grammar_path) == 0:
            print("Error: Unable to create grammar folder.")
            return

        file_count = 0
        full_ratio = 0.0
        none_ratio = 0.0
        avrg_ratio = 0.0

        # If src_dir is a directory then on_corpus_file() is invoked for every corpus file of the directory tree
        if os.path.isdir(src_dir):
            traverse_dir(src_dir, "", on_corpus_file, recreate_struct, True)

        # If src_dir is a file then simply call on_corpus_file() for it
        elif os.path.isfile(src_dir):
            on_corpus_file(src_dir)

        if file_count:
            full_ratio /= float(file_count)
            none_ratio /= float(file_count)
            avrg_ratio /= float(file_count)

        print("Total statistics\n-----------------\nCompletely parsed ratio: {0[0]}\n"
              "Completely unparsed ratio: {0[1]}\nAverage parsed ratio: {0[2]}".format(
                full_ratio,
                none_ratio,
                avrg_ratio))

    # ======================================================================================================
    # def parse_corpus_files(src_dir, dst_dir, dict_dir, grammar_dir, template_dir, linkage_limit, options):
    # ======================================================================================================
    if os.path.isfile(dict_dir) and dict_dir.endswith("4.0.dict"):
        on_dict_file(dict_dir)

    elif os.path.isdir(dict_dir):
        traverse_dir(dict_dir, "", on_dict_file, None, False)
