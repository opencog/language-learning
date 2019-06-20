import re
from typing import Optional
# from .pipelinetreenode import PipelineTreeNode2

__all__ = ['PipelineComponentException', 'FatalPipelineException']


class PipelineComponentException(Exception):
    """
    Class used to provide pipeline component exception information such as component configuration sequential number
        in JSON configuration file, run count number, related to 'specific-parameters' configuration sequential number
        (both are 1-based), exception class name (exception raised from within component) and traceback dump in case of
        unhandled exception.
    """
    def __init__(self, message: str, node = None,
                 t: Optional[object] = None, tb: Optional[str] = None):
        # super.__init__(self, message)
        self._message = message
        self._node = node
        self._component = node._component_name
        self._cfg_count = node.seq_no
        self._run_count = node._environment.get("RUN_COUNT", 0)
        self._exception = t
        self._traceback = tb

    @staticmethod
    def get_exception_name(exception_obj: Optional[Exception]) -> str:
        """
        Get exception class name string

        :param exception_obj:   Exception derived class object
        :return:                Exception class name or empty string if 'exception_obj' is None
        """
        if exception_obj is None:
            return ""

        name_pattern = re.compile("<class '(\w+)'>", re.S)
        result_list = re.findall(name_pattern, str(exception_obj.__class__))
        return result_list[0] if len(result_list) > 0 else ""

    def __str__(self):
        return f"{self._component}(cfg={self._cfg_count+1}, run={self._run_count}):\n" \
            f"{self.get_exception_name(self._exception)}: {self._message}\n" \
            f"Environment:\n{self._node._environment}\n" \
            f"Parameters:\n{self._node._parameters}"


class FatalPipelineException(Exception):
    pass
