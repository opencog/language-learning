import sys
import os
import logging
from subprocess import PIPE, Popen

from ..common.absclient import AbstractFileParserClient, AbstractProgressClient
from .optconst import *
from .psparse import *
from .parsestat import *
from ..common.parsemetrics import *
from .lgmisc import *
from .parsevaluate import get_parses, load_ull_file
from .commands import *
from .sentencecount import get_sentence_count
from .linkgrammarver import get_lg_version, get_lg_dict_version


__all__ = ['LGInprocParser']


class PSSentence:
    def __init__(self, sent_text):
        self.text = sent_text
        self.linkages = []
        self.valid = True

    def __str__(self):
        ret = self.text + "\n"

        for linkage in self.linkages:
            ret += linkage + "\n"

        return ret


class LGInprocParser(AbstractFileParserClient):

    def __init__(self, limit: int=100, timeout=1, verbosity=1):
        self._logger = logging.getLogger("LGInprocParser")
        self._linkage_limit = limit
        self._timeout = timeout
        self._out_stream = None
        self._ref_stream = None
        self._counter = 0
        self._lg_version, self._lg_dict_path = get_lg_version()
        self._lg_verbosity = verbosity

    def _parse_batch_ps_output(self, text: str, options: int) -> list:
        """
        Parse postscript returned by link-parser executable in a form where each sentence is followed by zero
            or many postscript notated linkages. Postscript linkages are usually represented by three lines
            enclosed in brackets.

        :param text:        String variable with postscript output returned by link-parser.
        :param options:     Parsing options.
        :return:            List of PSSentence.

        """
        sentences = []

        pos = skip_command_response(text)
        end = trim_garbage(text)

        if pos > end:
            end = text.rfind("No complete linkages found.")

        sent_count = 0

        validity_mask = (options & (BIT_EXCLUDE_TIMEOUTED | BIT_EXCLUDE_PANICED | BIT_EXCLUDE_EXPLOSION))

        # Parse output to get sentences and linkages in postscript notation
        for block in text[pos:end].split("\n\n"):

            block = block.strip()

            # Check if the LG output block contains only one parse
            parses = split_ps_parses(block)

            for sent in parses:

                # Get echoed sentence out of postscript output parse
                sentence = get_sentence_text(sent)

                # Get postscript starting position after parsing LG error and warning messages
                post_start, post_errors = skip_linkage_header(sent)

                # Check if the postscript linkage is valid
                is_valid = not (post_errors & validity_mask)

                # Successfully parsed sentence is added here
                cur_sent = PSSentence(sentence)

                cur_sent.valid = is_valid

                # Separate period with space if not already separated
                sentence = sentence[:-1] + " ." if sentence[-1:] == r"." else sentence

                postscript = sent[post_start:].replace("\n", "") if is_valid \
                    else r"[([" + r"])([".join(sentence.split(" ")) + r"])][][0]"

                cur_sent.linkages.append(postscript)
                sentences.append(cur_sent)

                sent_count += 1

        return sentences

    def _handle_stream_output(self, text: str, options: int, out_stream, ref_path: str) -> (ParseMetrics, ParseQuality):
        """
        Handle link-parser output stream text depending on options' BIT_OUTPUT field.

        :param text:        Stream output text.
        :param options:     Integer variable with multiple bit fields.
        :param out_stream:  Output file stream handle.
        :param ref_path:    Reference file path.
        :return:            Tuple (ParseMetrics, ParseQuality)
        """
        total_metrics, total_quality = ParseMetrics(), ParseQuality()

        ref_parses = []

        # Parse only if 'ull' output format is specified.
        if not (options & BIT_OUTPUT):

            if options & BIT_PARSE_QUALITY and ref_path is not None:
                data = load_ull_file(ref_path)

                try:
                    ref_parses = get_parses(data, (options & BIT_NO_LWALL) == BIT_NO_LWALL, False)

                except AssertionError as err:
                    raise LGParseError(str(err) + "\n\tMake sure '{}' has proper .ull file format.".format(ref_path))

            # Parse output into sentences and assotiate a list of linkages for each one of them.
            sentences = self._parse_batch_ps_output(text, options)

            with open("sentences.txt", "w") as file:
                for sentence in sentences:
                    print(sentence.text, file=file)
                    print(sentence.linkages, file=file)

            if options & BIT_PARSE_QUALITY and ref_path is not None:
                len_ref, len_par = len(ref_parses), len(sentences)

                if len(ref_parses) != len(sentences):
                    string = "\n".join([sent.text for sent in sentences])
                    self._logger.debug(string)
                    raise LGParseError("Number of sentences in corpus and reference files missmatch. "
                                       "Reference file '{}' does not match "
                                       "its corpus counterpart {} != {}.".format(ref_path, len_ref, len_par))

            sentence_count = 0

            # Parse linkages and make statistics estimation
            for sent in sentences:

                linkage_count = 0

                sent_metrics, sent_quality = ParseMetrics(), ParseQuality()

                # # If sentence, for some reason, can not be parsed
                # if not len(sent.linkages):
                #     # Print original sentence with no links in order for the sentence numbers
                #     #   in corpus and reference files to be exactly the same.
                #     print(sent.text + "\n", file=out_stream)

                # Parse and calculate statistics for each linkage
                for lnkg in sent.linkages:

                    if linkage_count == 1:  # Only the first linkage is taken into account so far
                        break

                    # Parse postscript notated linkage and get two lists with tokens and links in return.
                    tokens, links = parse_postscript(lnkg, options)

                    # prepared = None

                    if not len(tokens):
                        self._logger.warning(f"No tokens for sentence: '{lnkg.text}'")

                    # # If sentence, for some reason, can not be parsed
                    # if not len(tokens):
                    #     # Print original sentence with no links in order for the sentence numbers
                    #     #   in corpus and reference files to be exactly the same.
                    #     print(sent.text + "\n", file=out_stream)
                    # else:
                    #     # Print out links in ULL-format
                    #     print_output(tokens, links, options, out_stream)

                    # Print out links in ULL-format
                    print_output(tokens, links, options, out_stream)

                    if not sent.valid:
                        sent_metrics.skipped_sentences += 1
                        continue

                    # Calculate parseability statistics
                    prepared = prepare_tokens(tokens, options)
                    sent_metrics += parse_metrics(prepared)

                    # Calculate parse quality if the option is set
                    if sent.valid and (options & BIT_PARSE_QUALITY) and len(ref_parses):
                        sent_quality += parse_quality(get_link_set(tokens, links, options),
                                                      ref_parses[sentence_count][1])

                    linkage_count += 1

                assert sent_metrics.average_parsed_ratio <= 1.0, "sent_metrics.average_parsed_ratio > 1.0"
                assert sent_quality.quality <= 1.0, "sent_quality.quality > 1.0"

                total_metrics += sent_metrics
                total_quality += sent_quality

                sentence_count += 1

            total_metrics.sentences = sentence_count
            total_quality.sentences = sentence_count

        # If output format is other than ull then simply write text to the output stream.
        else:
            print(text, file=out_stream)

        return total_metrics, total_quality

    def parse(self, dict_path: str, corpus_path: str, output_path: str, ref_file: str, options: int,
              progress: AbstractProgressClient=None) \
            -> (ParseMetrics, ParseQuality):
        """
        Link parser invocation routine. Runs link-parser executable in a separate process.

        :param dict_path:       Name or path to the dictionary.
        :param corpus_path:     Path to the test text file.
        :param output_path:     Output file path.
        :param ref_file:        Reference file path.
        :param options:         Bit mask representing parsing options.
        :param progress:        Progress instance reference.
        :return:                Tuple (ParseMetrics, ParseQuality).
        """
        if progress is None:
            self._logger.info("Link Grammar version: {}\n"
                  "Link Grammar dictionaries: {}".format(self._lg_version, self._lg_dict_path))

        if not (options & BIT_EXISTING_DICT):
            dict_ver = get_lg_dict_version(dict_path)

            self._logger.warning(f"Dictionary version: {dict_ver}, link-parser version: {self._lg_version}")

            if dict_ver != "0.0.0" and (self._lg_version < "5.5.0" and dict_ver >= "5.5.0" or
                    self._lg_version >= "5.5.0" and dict_ver < "5.5.0"):
                raise LGParseError(f"Wrong dictionary version: {dict_ver}, expected: {self._lg_version}")

        sentence_count = 0

        bar = None

        if progress is None:
            self._logger.info("Parsing a corpus file: '" + corpus_path + "'")
            self._logger.info("Using dictionary: '" + dict_path + "'")

            if output_path is not None:
                self._logger.info("Parses are saved in: '" + output_path+get_output_suffix(options) + "'")
            else:
                self._logger.info("Output file name is not specified. Parses are redirected to 'stdout'.")

            if ref_file is not None:
                self._logger.info("Reference file: '" + ref_file + "'")
            else:
                self._logger.info("Reference file name is not specified. Parse quality is not calculated.")

        sed_rex = get_sed_regex(options)
        sed_cmd = ["sed", "-e", sed_rex, corpus_path]

        out_stream = None
        ret_metrics = ParseMetrics()
        ret_quality = ParseQuality()

        raw_stream, err_stream = None, None

        try:
            # Get number of sentences in input file
            sentence_count = get_sentence_count(corpus_path, options)

            if progress is not None:
                progress_type = type(progress)
                bar = progress_type(total=sentence_count, desc=os.path.split(corpus_path)[1],
                                    unit="sentences", leave=True)
            else:
                self._logger.info("Number of sentences: {}".format(sentence_count))

            lgp_cmd = get_linkparser_command(options, dict_path, self._linkage_limit, self._timeout, self._lg_verbosity)

            out_stream = sys.stdout if output_path is None \
                else open(output_path+get_output_suffix(options), "w", encoding="utf-8")

            with Popen(sed_cmd, stdout=PIPE) as proc_grep, \
                 Popen(lgp_cmd, stdin=proc_grep.stdout, stdout=PIPE, stderr=PIPE) as proc_pars:

                # Closing grep output stream will terminate it's process.
                proc_grep.stdout.close()

                # Read pipes to get complete output returned by link-parser
                raw_stream, err_stream = proc_pars.communicate()

                # with open(output_path + ".raw", "w") as r:
                #     r.write(raw_stream.decode("utf-8-sig"))
                #
                # with open(output_path + ".err", "w") as e:
                #     e.write(err_stream.decode("utf-8-sig"))

                # Check return code to make sure the process completed successfully.
                if proc_pars.returncode != 0:
                    raise ParserError("Process '{0}' terminated with exit code: {1} "
                                       "and error message:\n'{2}'.".format(lgp_cmd[0], proc_pars.returncode,
                                                                           err_stream.decode()))

                # Take an action depending on the output format specified by 'options'
                ret_metrics, ret_quality = self._handle_stream_output(raw_stream.decode("utf-8-sig"), options,
                                                                      out_stream, ref_file)

                if progress is not None:
                    progress.update(sentence_count)

                if bar is not None:
                    bar.update(sentence_count)

                if not (options & BIT_OUTPUT) and ret_metrics.sentences != sentence_count:
                    path_len = len(corpus_path)

                    raise LGParseError("Number of sentences does not match. "
                          "Read: {}, Parsed: {}, File: {}".format(sentence_count, ret_metrics.sentences,
                                                        corpus_path if path_len < 31 else
                                                        "..." + corpus_path[path_len-27:]))

                    # self._logger.warning("Number of sentences does not match. "
                    #       "Read: {}, Parsed: {}, File: {}".format(sentence_count, ret_metrics.sentences,
                    #                                     corpus_path if path_len < 31 else
                    #                                     "..." + corpus_path[path_len-27:]))

        except LGParseError as err:
            self._logger.debug(err_stream.decode("utf-8-sig"))

            with open(output_path + ".raw", "w") as r:
                r.write(raw_stream.decode("utf-8-sig"))

            with open(output_path + ".err", "w") as e:
                e.write(err_stream.decode("utf-8-sig"))

            raise

        except AssertionError as err:
            raise ParserError("Invalid statistics result. " + str(err))

        finally:
            if bar is not None:
                del bar

            if out_stream is not None and out_stream != sys.stdout:
                out_stream.close()

        return ret_metrics, ret_quality
