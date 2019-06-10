import os
import logging

from ..common.optconst import *
from ..common.textprogress import TextProgress
from ..common.cliutils import handle_path_string, strip_quotes
from ..common.absclient import AbstractPipelineComponent
from .artificialparser import SequentialParser, RandomParser
from .lginprocparser import LGInprocParser
from .grammartester import GrammarTester

__all__ = ['GrammarTesterComponent']

CONF_DICT_PATH = "input_grammar"
CONF_CORP_PATH = "input_corpus"
CONF_DEST_PATH = "output_path"
CONF_REFR_PATH = "ref_path"
CONF_GRMR_PATH = "grammar_root"
CONF_TMPL_PATH = "template_path"
CONF_LNK_LIMIT = "linkage_limit"
CONF_TIMEOUT = "timeout"


class GrammarTesterComponent(AbstractPipelineComponent):

    parser_types = {
        "random": RandomParser, "sequential": SequentialParser, "link-grammar-exe": LGInprocParser
    }

    def __init__(self, **kwargs):

        parser_type_str = kwargs.get("parser_type", "link-grammar-exe")

        if parser_type_str not in GrammarTesterComponent.parser_types:
            raise ValueError("Invalid 'parser_type' value.")

        parser_type = GrammarTesterComponent.parser_types.get(parser_type_str, LGInprocParser)

        # Create parser instance
        parser = parser_type(kwargs.get(CONF_LNK_LIMIT, 100), kwargs.get(CONF_TIMEOUT, 1))

        # Create GrammarTester instance
        self.tester = GrammarTester(handle_path_string(kwargs.get(CONF_GRMR_PATH, r"~/data/dict")),
                                    handle_path_string(kwargs.get(CONF_TMPL_PATH)),
                                    kwargs.get(CONF_LNK_LIMIT, 100), parser)

    def validate_parameters(self, **kwargs) -> bool:
        """ Validate configuration parameters """
        grammar_root = kwargs.get(CONF_GRMR_PATH, None)

        if grammar_root is not None and not os.path.isdir(grammar_root):
            raise FileNotFoundError(f"'{CONF_GRMR_PATH}' must be an existing directory path.")

        template_path = kwargs.get(CONF_TMPL_PATH, None)

        if template_path is not None and not os.path.isdir(template_path):
            raise FileNotFoundError(f"'{CONF_TMPL_PATH}' must be an existing directory path.")

        return True

    def run(self, **kwargs) -> dict:
        """ Execute component code """
        logger = logging.getLogger("GrammarTesterComponent.run")

        logger.debug(f"kwargs={kwargs}")

        options = get_options(kwargs)

        logger.debug(f"options=0x{hex(options)}")

        dict_param = kwargs.get(CONF_DICT_PATH, None)

        dict_path = "en" if dict_param is None \
            else (handle_path_string(dict_param) if not (options & BIT_EXISTING_DICT) else strip_quotes(dict_param))

        ref_path = kwargs.get(CONF_REFR_PATH, None)

        if ref_path:
            ref_path = handle_path_string(ref_path)

        pa, pq = self.tester.test(dict_path,
                         handle_path_string(kwargs.pop(CONF_CORP_PATH)),
                         handle_path_string(kwargs.pop(CONF_DEST_PATH, os.environ['PWD'])),
                         ref_path,
                         options, TextProgress, **kwargs)

        return {"parseability": pa.parseability_str(pa), "PA": pa.parseability_str(pa), "F1": pq.f1_str(pq),
                "recall": pq.recall_str(pq), "precision": pq.precision_str(pq), "PT": pa.parse_time_str(pa)}
