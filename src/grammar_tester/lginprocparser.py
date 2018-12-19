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
from .linkgrammarver import get_lg_version


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

        sent_count = 0

        validity_mask = (options & (BIT_EXCLUDE_TIMEOUTED | BIT_EXCLUDE_PANICED | BIT_EXCLUDE_EXPLOSION))

        # Parse output to get sentences and linkages in postscript notation
        for sent in text[pos:end].split("\n\n"):

            sent = sent.strip()

            # Get postscript starting position after parsing LG error and warning messages
            post_start, post_errors = skip_linkage_header(sent)

            # is_valid = post_start >= 0

            # Get input sentence(s) echoed by link-parser
            echo_text = sent if post_start < 0 else sent[:post_start-1]

            # There might be many sentences followed by single postscript if one or several sentences are not parsed
            #   because of so called 'combinatorial explosion'.
            lines = echo_text.split("\n")

            num_lines = len(lines)

            # If verbosity is set to 0
            if self._lg_verbosity == 0:

                # None of the unparsed by link-parser sentences, if any, should be missed
                for i in range(0, num_lines-1):
                    sent_text = lines[i]
                    tokens = sent_text.split(" ")
                    sent_obj = PSSentence(sent_text)

                    # Produce fake postscript in order for proper statistic estimation
                    post_text = r"[([" + r"])([".join(tokens) + r"])][][0]"
                    sent_obj.linkages.append(post_text)
                    sentences.append(sent_obj)

                sentence = lines[num_lines-1]

            else:
                sentence = lines[0]

            # Check if the postscript linkage is valid
            is_valid = not (post_errors & validity_mask)

            # Successfully parsed sentence is added here
            cur_sent = PSSentence(sentence)

            cur_sent.valid = is_valid

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

            if options & BIT_PARSE_QUALITY and ref_path is not None:
                if len(ref_parses) != len(sentences):
                    raise LGParseError("Number of sentences in corpus and reference files missmatch. "
                                       "Reference file '{}' does not match "
                                       "its corpus counterpart.".format(ref_path))

            sentence_count = 0

            # Parse linkages and make statistics estimation
            for sent in sentences:

                linkage_count = 0

                sent_metrics, sent_quality = ParseMetrics(), ParseQuality()

                # Parse and calculate statistics for each linkage
                for lnkg in sent.linkages:

                    if linkage_count == 1:  # Only the first linkage is taken into account so far
                        break

                    # Parse postscript notated linkage and get two lists with tokens and links in return.
                    tokens, links = parse_postscript(lnkg, options)

                    prepared = None

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

        sed_cmd = ["sed", "-e", get_sed_regex(options), corpus_path]

        out_stream = None
        ret_metrics = ParseMetrics()
        ret_quality = ParseQuality()

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
                raw, err = proc_pars.communicate()

                # Check return code to make sure the process completed successfully.
                if proc_pars.returncode != 0:
                    raise ParserError("Process '{0}' terminated with exit code: {1} "
                                       "and error message:\n'{2}'.".format(lgp_cmd[0], proc_pars.returncode,
                                                                           err.decode()))

                # with open(corpus_path+".raw", "w") as r:
                #     r.write(raw.decode("utf-8-sig"))
                #
                # with open(corpus_path+".err", "w") as e:
                #     e.write(err.decode("utf-8-sig"))

                # Take an action depending on the output format specified by 'options'
                ret_metrics, ret_quality = self._handle_stream_output(raw.decode("utf-8-sig"), options,
                                                                      out_stream, ref_file)

                if progress is not None:
                    progress.update(sentence_count)

                if bar is not None:
                    bar.update(sentence_count)

                if not (options & BIT_OUTPUT) and ret_metrics.sentences != sentence_count:
                    self._logger.warning("Number of sentences does not match. "
                          "Read: {}, Parsed: {}".format(sentence_count, ret_metrics.sentences))

        # except FileNotFoundError as err:
        #     print("FileNotFoundError: " + str(err))
        #     raise ParserError(err)

        # except LGParseError as err:
        #     print("LGParseError: " + str(err))
        #     raise ParserError(err)

        except AssertionError as err:
            raise ParserError("Invalid statistics result. " + str(err))

        finally:
            if bar is not None:
                del bar

            if out_stream is not None and out_stream != sys.stdout:
                out_stream.close()

        return ret_metrics, ret_quality
