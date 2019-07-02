import sys
import os
import logging
from typing import Union
from subprocess import PIPE, Popen

from ..common.sedcommands import *
from ..common.parsemetrics import *
from ..common.sentencecount import get_sentence_count
from ..common.absclient import AbstractFileParserClient, AbstractProgressClient

from .lgdatastructures import AbstractStreamParser, AbstractLGStreamParser
from .lgparsequalityestimator import LGParseQualityEstimator

from ..grammar_tester.lgmisc import *
from ..grammar_tester.lgpcommands import *
from ..grammar_tester.linkgrammarver import get_lg_version
from ..grammar_tester.parsevaluate import EvalError


__all__ = ['LGInprocParser2']


class LGDefaultStreamParser(AbstractStreamParser):

    def on_data(self, text: str, options: int):
        print(text)


class LGInprocParser2(AbstractFileParserClient):
    """
    Link Grammar Parser implicitly running link-parser executable in a separate process.
    """
    def __init__(self, limit: int=100, timeout: int=1, lg_verbosity: int=1):
        self._lg_version, self._lg_dict_path = get_lg_version()
        self._logger = logging.getLogger("LGInprocParser2")
        self._parser = LGInprocParserX(limit, timeout, lg_verbosity)

    def parse(self, dict_path: str, corpus_path: str, output_path: str, ref_file: str, options: int,
              progress: AbstractProgressClient = None, **kwargs) \
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
            self._logger.info(f"Parsing a corpus file: '{corpus_path}'")
            self._logger.info(f"Using dictionary: '{dict_path}'")

            if output_path is not None:
                self._logger.info(f"Parses are saved in: '{output_path}'")
            else:
                self._logger.info("Output file name is not specified. Parses are redirected to 'stdout'.")

            if ref_file is not None:
                self._logger.info(f"Reference file: '{ref_file}'")
            else:
                self._logger.info("Reference file name is not specified. Parse quality is not calculated.")

        # Get number of sentences in input file
        sentence_count = get_sentence_count(corpus_path, options)

        bar = None

        if progress is not None:
            progress_type = type(progress)
            bar = progress_type(total=sentence_count, desc=os.path.split(corpus_path)[1],
                                unit="sentences", leave=True)
        else:
            self._logger.info(f"Number of sentences: {sentence_count}")

        out_stream = None
        ref_stream = None

        ret_metrics = ParseMetrics()
        ret_quality = ParseQuality()

        try:
            out_stream = sys.stdout if output_path is None \
                else open(output_path, "w", encoding="utf-8")

            ref_stream = None if ref_file is None or len(ref_file) == 0 \
                else open(ref_file, "r", encoding="utf-8")

            if progress is not None:
                progress.update(sentence_count)

            if bar is not None:
                bar.update(sentence_count)

            # Need class fabric to handle output formats other than ULL

            # Create postscript parser instance
            proto = LGParseQualityEstimator(options, out_stream, ref_stream) if not (options & BIT_OUTPUT) \
                else LGDefaultStreamParser()

            self._parser.parse(dict_path, corpus_path, options, proto)

            if hasattr(proto, "get_pa_pq"):
                ret_metrics, ret_quality = proto.get_pa_pq()

            if not (options & BIT_OUTPUT) and ret_metrics.sentences != sentence_count:
                self._logger.warning(f"Number of sentences does not match. "
                                     f"Read: {sentence_count}, Parsed: {ret_metrics.sentences}")

            return ret_metrics, ret_quality

        except EvalError as err:
            raise LGParseError(err)

        finally:
            if bar is not None:
                del bar

            if out_stream is not None and out_stream != sys.stdout:
                out_stream.close()

            if ref_stream is not None:
                ref_stream.close()


class LGInprocParserX():
    """
    Link Grammar Parser implicitly running link-parser executable in a separate process.
    """
    def __init__(self, limit: int=100, timeout: int=1, lg_verbosity: int=1, num_linkages: int=1):

        self._logger = logging.getLogger("LGInprocParserX")
        self._linkage_limit = limit
        self._timeout = timeout
        self._counter = 0
        self._lg_verbosity = lg_verbosity
        self._num_linkages = num_linkages

    def parse(self, dict_path: str, corpus_path: str, options: int,
              stream_parser: Union[AbstractLGStreamParser, None]=LGDefaultStreamParser()) -> None:
        """
        Link parser invocation routine. Runs link-parser executable in a separate process.

        :param dict_path:       Name or path to the dictionary.
        :param corpus_path:     Path to the test text file.
        :param output_path:     Output file path.
        :param ref_file:        Reference file path.
        :param options:         Bit mask representing parsing options.
        :param stream_parser:   Instance of AbstractLGStreamParser derived class.
        :return:                None.
        """
        sed_cmd = get_sed_cmd_common_part(options) + [corpus_path]

        try:
            lgp_cmd = get_linkparser_command(options, dict_path, self._linkage_limit, self._timeout, self._lg_verbosity,
                                             self._num_linkages)

            with Popen(sed_cmd, stdout=PIPE) as proc_grep, \
                 Popen(lgp_cmd, stdin=proc_grep.stdout, stdout=PIPE, stderr=PIPE) as proc_pars:

                # Closing grep output stream will terminate it's process.
                proc_grep.stdout.close()

                # Read pipes to get complete output returned by link-parser
                raw_stream, err_stream = proc_pars.communicate()

                # Check return code to make sure the process completed successfully.
                if proc_pars.returncode != 0:
                    raise ParserError(f"Process '{lgp_cmd[0]}' terminated with exit code: {proc_pars.returncode} "
                                      f"and error message:\n'{err_stream.decode()}'.")

                # Run stream parser if it is not None
                if stream_parser is not None:
                    stream_parser.on_data(raw_stream.decode("utf-8-sig"), options)

        # except LGParseError as err:
        #     self._logger.debug(err_stream.decode("utf-8-sig"))
        #
        #     with open(output_path + ".raw", "w") as r:
        #         r.write(raw_stream.decode("utf-8-sig"))
        #
        #     with open(output_path + ".err", "w") as e:
        #         e.write(err_stream.decode("utf-8-sig"))
        #
        #     raise

        except AssertionError as err:
            raise ParserError("Invalid statistics result. " + str(err))

        except EvalError as err:
            raise LGParseError(err)
