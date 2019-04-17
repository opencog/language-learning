from typing import Optional

__all__ = ['PipelineComponentException', 'FatalPipelineException']


class PipelineComponentException(Exception):

    def __init__(self, message: str, component: str="", config_count: int=0, run_count: int=0,
                 t: Optional[object]=None):
        # super.__init__(self, message)
        self._message = message
        self._component = component
        self._cfg_count = config_count
        self._run_count = run_count

    def __str__(self):
        return f"{self._component}({self._cfg_count})({self._run_count}):{self._message}"


class FatalPipelineException(Exception):
    pass
