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
              progress: AbstractProgressClient = None, **kwargs) -> (ParseMetrics, ParseQuality):
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

