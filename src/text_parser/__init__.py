import logging
from typing import Union
from ..common.absclient import AbstractPipelineComponent, AbstractFileParserClient, AbstractProgressClient
from ..common.cliutils import handle_path_string
from ..common.parsemetrics import ParseMetrics, ParseQuality
from ..common.optconst import get_options
from ..grammar_tester.lginprocparser import LGInprocParser
from ..grammar_tester.parsevaluate import compare_ull_files

from ..grammar_tester.gt_component import GrammarTesterComponent

__all__ = ['TextParserComponent']

# __all__.extend(learner.__all__)

PARAM_LANGUAGE  = 'language'
PARAM_DICT_PATH = 'dict_path'
PARAM_CORP_PATH = 'corpus_path'
PARAM_OUTP_PATH = 'output_path'
PARAM_REFR_PATH = 'ref_path'
PARAM_OPTIONS   = 'options'
PARAM_PARS_TYPE = 'parser_type'
PARAM_PARS_LIMIT    = 'linkage_limit'
PARAM_PARS_TIMEOUT  = 'lg_timeout'


class TextParserComponent(GrammarTesterComponent):
    """
    Temporary stub for TextParserComponent made out of GrammarTesterComponent because of the similar
    functionality of the later. It helps to keep argument checking and directory tree traversing code
    in one place.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# def check_kwargs(**kwargs):
#     print(kwargs)
#
# class TextParserComponent(AbstractPipelineComponent):
#
#     parser_types = ["random", "sequential", "link-grammar-exe"]
#
#     def __init__(self, **kwargs):
#         # check_kwargs(**kwargs)
#         pass
#
#     def validate_parameters(self, **kwargs):
#         """ Validate configuration parameters """
#         logger = logging.getLogger("TextParserComponent.validate_parameters")
#
#         ret_val = True
#
#         parser_type: str = kwargs.get(PARAM_PARS_TYPE, None)
#
#         if parser_type is None:
#             logger.error(f"Required parameter '{PARAM_PARS_TYPE}' is not specified.")
#             ret_val = False
#
#         if parser_type not in TextParserComponent.parser_types:
#             logger.error(f"Illegal '{PARAM_PARS_TYPE}' value. '{PARAM_PARS_TYPE}' must be one of: "
#                              f"{','.join(TextParserComponent.parser_types)}")
#             ret_val = False
#
#         if kwargs.get(PARAM_CORP_PATH, None) is None:
#             logger.error(f"Parameter '{PARAM_CORP_PATH}' is not specified.")
#             ret_val = False
#
#         if kwargs.get(PARAM_OUTP_PATH, None) is None:
#             logger.error(f"Parameter '{PARAM_OUTP_PATH}' is not specified.")
#             ret_val = False
#
#         if parser_type.startswith("link-grammar"):
#
#             if kwargs.get(PARAM_DICT_PATH, None) is None and kwargs.get(PARAM_LANGUAGE, None) is None:
#                 logger.error("Error: neither '{}' nor '{}' is specified.".format(PARAM_DICT_PATH, PARAM_LANGUAGE))
#                 ret_val = False
#
#         return ret_val
#
#     @staticmethod
#     def _get_parser(**kwargs) -> Union[AbstractFileParserClient, None]:
#         """ Return AbstractFileParserClient instance """
#         parser_type = kwargs.get(PARAM_PARS_TYPE, None)
#
#         if parser_type is None:
#             return LGInprocParser()
#
#         elif parser_type is "link-parser-exe":
#             limit = kwargs.get(PARAM_PARS_LIMIT, 1000)
#             timeout = kwargs.get(PARAM_PARS_TIMEOUT, 1)
#             return LGInprocParser(limit, timeout)
#
#     def run(self, **kwargs):
#         """ Execute component code """
#
#         # Create parser instance
#         parser = self._get_parser(**kwargs)
#
#         # Convert text parameters into integer
#         options = get_options(kwargs)
#
#         language = kwargs.get(PARAM_LANGUAGE, None)
#         dict_path = kwargs.get(PARAM_DICT_PATH, None)
#
#         dict_path = language if language is not None else "en" if dict_path is None \
#             else handle_path_string(dict_path)
#
#         refr_path = kwargs.get(PARAM_REFR_PATH)
#
#         if refr_path is not None:
#             refr_path = handle_path_string(refr_path)
#
#         # Run parser
#         parser.parse(
#             dict_path,
#             handle_path_string(kwargs.pop(PARAM_CORP_PATH, None)),
#             handle_path_string(kwargs.pop(PARAM_OUTP_PATH, None)),
#             refr_path,
#             options
#         )
