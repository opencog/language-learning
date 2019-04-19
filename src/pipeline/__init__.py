from .varhelper import *
from .pipelinetreenode import *
from .pipelinetree import *
from .pipelineexceptions import *

__all__ = []
__all__.extend(varhelper.__all__)
__all__.extend(pipelinetreenode.__all__)
__all__.extend(pipelinetree.__all__)
__all__.extend(pipelineexceptions.__all__)


import os
from ..common.absclient import AbstractPipelineComponent
from ..common.cliutils import handle_path_string
from ..common.optconst import *
from ..common.tokencount import *


PARAM_INPUT_PATH            = 'input_path'
PARAM_OUTPUT_PATH           = 'output_path'


class PathCreatorComponent(AbstractPipelineComponent):
    """
    Path Creator Component responsible for creating directory structures

    """
    def __init__(self):
        pass

    def validate_parameters(self, **kwargs):
        return True

    def run(self, **kwargs):
        return {}

    @staticmethod
    def create(**kwargs):
        path = kwargs.get("path", None)

        if path is not None and not os.path.isdir(path):
            os.makedirs(path)

        return {"path": path}


class TokenCounterComponent(AbstractPipelineComponent):
    """
    Token Counter Component is responsible for counting token appearances in the corpus.

    """
    def __init__(self, **kwargs):
        # check_kwargs(**kwargs)
        pass

    def validate_parameters(self, **kwargs):
        """ Validate configuration parameters """
        ret_val = True

        if kwargs.get(PARAM_INPUT_PATH, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_INPUT_PATH))
            ret_val = False

        if kwargs.get(PARAM_OUTPUT_PATH, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_OUTPUT_PATH))
            ret_val = False

        return ret_val

    def run(self, **kwargs):
        """ Execute component code """

        options = get_options(kwargs)

        input_path = kwargs.get(PARAM_INPUT_PATH, None)

        if input_path:
            input_path = handle_path_string(input_path)

        output_path = kwargs.get(PARAM_OUTPUT_PATH, None)

        if output_path:
            output_path = handle_path_string(output_path)

        # Run Token Counter
        dump_token_counts(input_path, output_path, options)

        return {}
