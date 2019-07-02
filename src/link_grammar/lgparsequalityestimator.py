from .lgdatastructures import PQSentenceParse, Linkage

from .lgpsstreamparser import LGPSStreamParser, BreakCycle, ContinueCycle

from ..common.optconst import *
from ..grammar_tester.psparse import *
from ..grammar_tester.parsestat import *
from ..common.parsemetrics import *
from ..grammar_tester.lgmisc import *
from ..grammar_tester.parsevaluate import extract_parses, SentenceError, EvalError


class LGParseQualityEstimator(LGPSStreamParser):

    def __init__(self, options: int, out_stream, ref_stream=None):

        super().__init__()
        self._options = options
        self._ref_stream = ref_stream
        self._ref_parses = []
        self._parse_metrics = ParseMetrics()
        self._parse_quality = ParseQuality()
        self._sentence_count = 0
        self._out_stream = out_stream

        # Should parse quality be estimated...
        if self._options & BIT_PARSE_QUALITY and self._ref_stream is not None:

            try:
                # Load reference file contents
                data = self._ref_stream.read()

                # Read in reference parses
                self._ref_parses = extract_parses(data)

            except SentenceError as err:
                raise EvalError(str(err), self._ref_stream.name)

    def setup(self):
        if self._options & BIT_PARSE_QUALITY and self._ref_stream is not None:

            ref_len, prs_len = len(self._ref_parses), len(self._sentence_parses)

            if ref_len != prs_len:
                raise LGParseError(f"Number of sentences in corpus ({prs_len}) and reference ({ref_len}) files missmatch. "
                                   f"Reference file '{self._ref_stream.name}' does not match its corpus counterpart.")

        self._sentence_count = 0

    def cleanup(self):
        # self._parse_metrics.sentences = self._sentence_count
        # self._parse_quality.sentences = self._sentence_count
        pass

    def on_sentence_init(self, sentence: PQSentenceParse):
        sentence.linkage_count = 0
        sentence.parse_metrics = ParseMetrics()
        sentence.parse_quality = ParseQuality()

    def on_sentence_done(self, sentence: PQSentenceParse):
        assert sentence.parse_metrics.average_parsed_ratio <= 1.0, "sent_metrics.average_parsed_ratio > 1.0"
        assert sentence.parse_quality.quality <= 1.0, "sent_quality.quality > 1.0"

        self._parse_metrics += sentence.parse_metrics
        self._parse_quality += sentence.parse_quality

        self._sentence_count += 1

    def on_linkage_init(self, sentence: PQSentenceParse, linkage: Linkage):
        if sentence.linkage_count == 1:
            raise BreakCycle()

    def on_parsed_linkage(self, sentence: PQSentenceParse, linkage: Linkage):

        # Print out links in ULL-format
        print_output(linkage.tokens, linkage.links, self._options, self._out_stream)

        if not sentence.valid:
            sentence.parse_metrics.skipped_sentences += 1
            raise ContinueCycle()

        # Calculate parseability statistics
        pm = sentence.parse_metrics
        pm += parse_metrics(prepare_tokens(linkage.tokens, self._options))

        sentence.parse_metrics = pm

        # Calculate parse quality if the option is set
        if sentence.valid and (self._options & BIT_PARSE_QUALITY) and len(self._ref_parses):
            pq = sentence.parse_quality
            pq += parse_quality(get_link_set(linkage.tokens, linkage.links, self._options),
                                          self._ref_parses[self._sentence_count][1])
            sentence.parse_quality = pq

        # sentence.linkage_count += 1

    def on_linkage_done(self, sentence: PQSentenceParse, linkage: Linkage):
        pass

    def get_pa_pq(self) -> (ParseMetrics, ParseQuality):
        return self._parse_metrics, self._parse_quality
