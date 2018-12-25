import logging
import sys
import os

__all__ = ['strip_quotes', 'strip_trailing_slash', 'handle_path_string', 'strip_brackets', 'setup_logging',
           'VERBOSITY_OPTIONS']

VERBOSITY_OPTIONS = {"none": logging.NOTSET, "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
                     "error": logging.ERROR, "critical": logging.CRITICAL}


def setup_logging(console_level: int = logging.WARNING, file_level: int = logging.NOTSET, file_path: str = "error.log",
                  mode: str = "w") -> None:
    """
    Setup application logging

    :param console_level:       Logging level for console handler.
    :param file_level:          Logging level for file handler.
    :param file_path:           Log file path.
    :param mode:                Log file write mode.
    :return:                    None
    """
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Setup stream handler 'stdout'
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(console_level)
    logger.addHandler(stream)

    # No need to setup file handler if 'file_level' is logging.NOTSET
    if file_level > logging.NOTSET:
        # Setup log file handler
        file = logging.FileHandler(file_path, mode)
        file.setLevel(file_level)
        file.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file)


def strip_brackets(text) -> str:
    """
    Strips starting and trailing brackets from input string

    :param text: Text string to strip the brackets from.
    :return: Text string without brackets.
    """
    if text is None:
        return ""

    if text.startswith("[") and text.endswith("]"):
        return text[1:len(text) - 1]

    return text


def strip_quotes(text) -> str:
    """
    Strips starting and trailing quotes from input string

    :param text: Text string to strip the quotes from.
    :return: Text string without quotes.
    """
    if text is None:
        return ""

    l = len(text)

    if l == 0:
        return text

    start = 0 if text[0] != "'" and text[0] != '"' else 1
    end = l if text[l-1] != "'" and text[l-1] != '"' else l-1

    return text[start:end]


def strip_trailing_slash(text) -> str:
    """
    Strip trailing slash if any.

    :param text: Path string
    :return: Path string without trailing slash.
    """
    if text is None:
        return ""

    l = len(text)

    if not l:
        return ""

    end = l-1 if text[l-1] == "/" else l
    return text[:end]


def handle_path_string(text, cur_dir_subst: bool=True) -> str:
    """
    Strip off single or double quotes if any, replace tilda with home directory path
        and finally strip trailing slash if any.

    :param text: Path string.
    :return: Path string prepared to be used as an input parameter to any other function.
    """
    path = strip_trailing_slash(strip_quotes(text))

    if path.startswith("~"):
        path = path.replace("~", os.environ['HOME'])
    elif not path.startswith("/") and cur_dir_subst:
        path = os.environ['PWD'] + "/" + path

    return path
