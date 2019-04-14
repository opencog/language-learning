from ..common.absclient import AbstractPipelineComponent
from ..common.cliutils import handle_path_string
from .learner import *

__all__ = ['GrammarLearnerComponent']

__all__.extend(learner.__all__)

PARAM_INPUT_PARSES          = 'input_parses'
PARAM_OUTPUT_CATEGORIES     = 'output_categories'
PARAM_OUTPUT_GRAMMAR        = 'output_grammar'
PARAM_OUTPUT_STATISTICS     = 'output_statistics'
PARAM_TEMP_DIR              = 'temp_dir'


def check_kwargs(**kwargs):
    print(kwargs)

class GrammarLearnerComponent(AbstractPipelineComponent):

    def __init__(self, **kwargs):
        # check_kwargs(**kwargs)
        pass

    def validate_parameters(self, **kwargs):
        """ Validate configuration parameters """
        ret_val = True

        if kwargs.get(PARAM_INPUT_PARSES, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_INPUT_PARSES))
            ret_val = False

        if kwargs.get(PARAM_OUTPUT_CATEGORIES, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_OUTPUT_CATEGORIES))
            ret_val = False

        if kwargs.get(PARAM_OUTPUT_GRAMMAR, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_OUTPUT_GRAMMAR))
            ret_val = False

        if kwargs.get(PARAM_OUTPUT_STATISTICS, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_OUTPUT_STATISTICS))
            ret_val = False

        if kwargs.get(PARAM_TEMP_DIR, None) is None:
            print("Error: parameter '{}' is not specified.".format(PARAM_TEMP_DIR))
            ret_val = False

        return ret_val

    def run(self, **kwargs):
        """ Execute component code """

        # check_kwargs(**kwargs)

        # Run Grammar Learner
        return learn_grammar(**kwargs)
