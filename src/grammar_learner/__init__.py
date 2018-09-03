from ..common.absclient import AbstractPipelineComponent
from ..common.cliutils import handle_path_string
# from .learner import *
# from .learner import learn_grammar

__all__ = ['GrammarLearnerComponent']

# __all__ = ['GrammarLearnerComponent']
#
# __all__.extend(learner.__all__)


def check_kwargs(**kwargs):
    print(kwargs)

class GrammarLearnerComponent(AbstractPipelineComponent):

    def __init__(self, **kwargs):
        check_kwargs(**kwargs)

    def validate_parameters(self, **kwargs):
        """ Validate configuration parameters """
        return True

    def run(self, **kwargs):
        """ Execute component code """
        pass