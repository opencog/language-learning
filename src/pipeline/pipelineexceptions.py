__all__ = ['PipelineComponentException', 'FatalPipelineException']


class PipelineComponentException(Exception):
    pass


class FatalPipelineException(Exception):
    pass
