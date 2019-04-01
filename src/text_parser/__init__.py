from typing import Union
from ..common.absclient import AbstractPipelineComponent, AbstractFileParserClient
from ..common.cliutils import handle_path_string
from ..grammar_tester.lginprocparser import LGInprocParser
from ..common.optconst import get_options

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


def check_kwargs(**kwargs):
    print(kwargs)


class TextParserComponent(AbstractPipelineComponent):

    def __init__(self, **kwargs):
        # check_kwargs(**kwargs)
        pass

    def validate_parameters(self, **kwargs):
        """ Validate configuration parameters """
        ret_val = True

        if kwargs.get(PARAM_DICT_PATH, None) is None and \
            kwargs.get(PARAM_LANGUAGE, None) is None:
            print("Error: neither '{}' nor '{}' is specified.".format(PARAM_DICT_PATH, PARAM_LANGUAGE))
            ret_val = False

        if kwargs.get(PARAM_CORP_PATH, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_CORP_PATH))
            ret_val = False

        if kwargs.get(PARAM_OUTP_PATH, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_OUTP_PATH))
            ret_val = False

        return ret_val

    @staticmethod
    def _get_parser(**kwargs) -> Union[AbstractFileParserClient, None]:
        """ Return AbstractFileParserClient instance """
        parser_type = kwargs.get(PARAM_PARS_TYPE, None)

        if parser_type is None:
            return LGInprocParser()

        elif parser_type is "link-parser-exe":
            limit = kwargs.get(PARAM_PARS_LIMIT, 1000)
            timeout = kwargs.get(PARAM_PARS_TIMEOUT, 300)
            return LGInprocParser(limit, timeout)

    def run(self, **kwargs):
        """ Execute component code """

        # check_kwargs(**kwargs)

        # Create parser instance
        parser = self._get_parser(**kwargs)

        # Convert text parameters into integer
        options = get_options(kwargs)

        language = kwargs.get(PARAM_LANGUAGE, None)
        dict_path = kwargs.get(PARAM_DICT_PATH, None)

        dict_path = language if language is not None else "en" if dict_path is None else handle_path_string(dict_path)

        refr_path = kwargs.get(PARAM_REFR_PATH)

        if refr_path is not None:
            refr_path = handle_path_string(refr_path)

        # Run parser
        parser.parse(
            dict_path,
            handle_path_string(kwargs.pop(PARAM_CORP_PATH, None)),
            handle_path_string(kwargs.pop(PARAM_OUTP_PATH, None)),
            refr_path,
            options
        )
