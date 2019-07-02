from abc import abstractmethod, ABCMeta
from typing import List, Tuple, Optional
from ..common.parsemetrics import ParseMetrics, ParseQuality


class Linkage:

    def __init__(self, text: str):   # , tokens: Union[List[str], None]=None, links: Union[List[str], None]=None):
        self.linkage_text: str = text
        self.tokens: Optional[List[str]] = None
        self.links: Optional[List[Tuple[int, int]]] = None
        self.ignored_link_count: int = 0


class SentenceParse:
    """
    Class to store parses
    """
    def __init__(self, sent_text):
        self.text: str = sent_text
        self.linkages: List[Linkage] = []
        self.valid: bool = True
        self.linkage_count = 0

    def __str__(self):
        ret = self.text + "\n"

        for linkage in self.linkages:
            ret += linkage.linkage_text + "\n"

        return ret


class PQSentenceParse(SentenceParse):
    """
    Class to store parses along with parse statistics
    """
    def __init__(self, text):
        super().__init__(text)
        self.parse_metrics: Optional[ParseMetrics, None] = None
        self.parse_quality: Optional[ParseQuality, None] = None


class AbstractStreamParser(metaclass=ABCMeta):

    @abstractmethod
    def on_data(self, text: str, options: int):
        """ Called when buffer is filled with parses to process """
        pass


class AbstractLGStreamParser(AbstractStreamParser):
    """
    Base class for link-parser stream output
    """
    @abstractmethod
    def setup(self):
        """ Called to initialize all necessary data to start parsing stream data """
        pass

    @abstractmethod
    def cleanup(self):
        """ Called to clean up after stream parsing is done """
        pass

    @abstractmethod
    def on_sentence_init(self, sentence: SentenceParse) -> bool:
        """ Called to initialize SentenceParse instance """
        pass

    @abstractmethod
    def on_sentence_done(self, sentence: SentenceParse) -> bool:
        """ Called to clean up SentenceParse instance """
        pass

    @abstractmethod
    def on_linkage_init(self, sentence: SentenceParse, linkage: Linkage) -> bool:
        """ Called to perform all necessary initialization before linkage parsing is started """
        pass

    @abstractmethod
    def on_parsed_linkage(self, sentence: SentenceParse, linkage: Linkage) -> bool:
        """ Called when linkage is completely parsed and lists with tokens and links are prepared """
        pass

    @abstractmethod
    def on_linkage_done(self, sentence: SentenceParse, linkage: Linkage) -> bool:
        """ Called to perform clean up after linkage parsing is done """
        pass
