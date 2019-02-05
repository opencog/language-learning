from abc import ABCMeta, abstractmethod
from typing import List, Set, Tuple, Optional, Union

"""
    Abstract classes for service client definitions.
    
"""

from .parsemetrics import ParseMetrics, ParseQuality


__all__ = ['DashboardError', 'AbstractDashboardClient', 'AbstractConfigClient', 'AbstractGrammarTestClient',
           'AbstractFileParserClient', 'AbstractStatEventHandler', 'AbstractPipelineComponent',
           'AbstractProgressClient']

DASH_UPDATE_PARSEABILITY = 1
DASH_UPDATE_PARSEQUALITY = 2
DASH_UPDATE_ALL = DASH_UPDATE_PARSEABILITY | DASH_UPDATE_PARSEQUALITY


class DashboardError(Exception):
    pass


class AbstractDashboardClient(metaclass=ABCMeta):
    """
    Base class for publishing parse results to abstract dashboard which can be either file, or Web service,
        or spreadsheet.
    """
    @abstractmethod
    def set_cell_by_indexes(self, row_index: int, col_index: int, value: object):
        pass

    @abstractmethod
    def set_cell_by_names(self, row_name: str, col_name: str, value: object):
        pass

    @abstractmethod
    def update_dashboard(self):
        """ Update dashboard values """
        pass


class AbstractConfigClient(metaclass=ABCMeta):
    """
    Base class for classes responsible for obtaining configuration information either from files
        or from Web services
    """
    @abstractmethod
    def get_config(self, config_name: str, comp_name: str) -> dict:
        """
        Retreave configuration from whatever source.

        :param config_name:     Configuration name string.
        :param comp_name:       Component name string.
        :return:                Dictionary instance holding configuration parameters.
        """
        pass

    @abstractmethod
    def save_config(self, config_name: str, comp_name: str) -> None:
        """
        Save configuration to whatever destination.

        :param config_name:     Configuration name string.
        :param comp_name:       Component name string.
        :return:                None
        """
        pass


class AbstractProgressClient(metaclass=ABCMeta):
    """
    Base class for progress reporting client
    """
    @abstractmethod
    def update(self, increment: int) -> None:
        pass

    @abstractmethod
    def set_total(self, total: int) -> None:
        pass


class AbstractGrammarTestClient(metaclass=ABCMeta):
    """
    Base class responsible for induced grammar testing.
    """
    @abstractmethod
    def test(self, dict_path: str, corpus_path: str, output_path: str, reference_path: str, options: int,
             progress: AbstractProgressClient = None) -> (ParseMetrics, ParseQuality):
        pass


class AbstractFileParserClient(metaclass=ABCMeta):
    """
    Base class for parsers
    """
    @abstractmethod
    def parse(self, dict_path: str, corpus_path: str, output_path: str, ref_file: str, options: int,
              progress: AbstractProgressClient = None) -> (ParseMetrics, ParseQuality):
        pass


class AbstractStatEventHandler(metaclass=ABCMeta):
    """
    Base class for statistics event handlers
    """
    @abstractmethod
    def on_statistics(self, nodes: list, metrics: ParseMetrics, quality: ParseQuality) -> None:
        pass


class AbstractPipelineComponent(metaclass=ABCMeta):
    """
    Base class for pipe line components
    """
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """ This is a place holder for parameter checking and validation. Exceptions should not be generated in case
            of invalid parameter in order to let other components to check their parameters during a single run. The
            method should check all of the parameters print error messages and return False if at least one parameter
            is invalid.
        """
        pass

    @abstractmethod
    def run(self, **kwargs) -> dict:
        """ Run component execution. In case of severe errors exceptions should be raised to stop pipeline execution """
        pass


class Linkage:

    def __init__(self, text: str):   # , tokens: Union[List[str], None]=None, links: Union[List[str], None]=None):
        self.linkage_text: str = text
        self.tokens: List[str] = None
        self.links: List[Tuple[int, int]] = None
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


class AbstractSerializer(metaclass=ABCMeta):
    """
    Base class for serialization to be used by LG parsers
    """
    @abstractmethod
    def open(self):
        """ Open data storage """
        pass

    @abstractmethod
    def close(self):
        """ Close data storage """
        pass

    @abstractmethod
    def read(self):
        """ Read a single record/datum """
        pass

    @abstractmethod
    def write(self, record):
        """ Write a single record/datum """
        pass

    @abstractmethod
    def load(self):
        """ Deserialize data from a storage """
        pass

    @abstractmethod
    def dump(self, data_structure):
        """ Serialize data to a storage """
        pass


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
