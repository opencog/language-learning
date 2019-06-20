from typing import Tuple, List, Callable

from ..common.absclient import AbstractProgressClient, AbstractFileParserClient
from ..common.parsemetrics import ParseQuality, ParseMetrics
from ..common.optconst import *
from .parsevaluate import load_parses, save_parses, eval_parses, \
    make_sequential, make_random


__all__ = ['SequentialParser', 'RandomParser']


class ArtificialParser(AbstractFileParserClient):
    """
    Parser stub for random and sequential parsers

    """
    def __init__(self, operation: Callable[[List[Tuple[str, set]], int], List[Tuple[str, set]]], **kwargs):
        self.operation: callable = operation
        self.kwargs = kwargs

    def parse(self, dict_path: str, corpus_path: str, output_path: str, ref_file: str, options: int,
              progress: AbstractProgressClient = None, **kwargs) -> (ParseMetrics, ParseQuality):

        if self.operation is None:
            raise ValueError("Parse function reference is not set.")

        if (options & BIT_OUTPUT):
            raise ValueError("Only '.ull' output format is supported for specified 'parser_type'.")

        pm: ParseMetrics = ParseMetrics()

        ref_parses = load_parses(ref_file)
        test_parses = self.operation(ref_parses, options, **self.kwargs)
        save_parses(test_parses, output_path, options)

        # Here comes parse evaluation
        pq = eval_parses(test_parses, ref_parses, options)[0]

        pm.skipped_sentences = pq.skipped_sentences

        return pm, pq


class SequentialParser(ArtificialParser):
    def __init__(self, limit: int = 100, timeout=1, verbosity=1):
        super().__init__(make_sequential, limit = limit, timeout=timeout, verbosity=verbosity)


class RandomParser(ArtificialParser):
    def __init__(self, limit: int = 100, timeout=1, verbosity=1):
        super().__init__(make_random, limit = limit, timeout=timeout, verbosity=verbosity)
