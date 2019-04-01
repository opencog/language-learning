from typing import List
from ..common.optconst import *


def get_linkparser_command(options: int, dict_path: str, limit: int, timeout: int, verb: int=1, num_linkages: int=1) \
        -> List[str]:

    verbosity = "-verbosity={}".format(verb)

    # Make command option list depending on the output format specified.
    if not (options & BIT_OUTPUT) or (options & BIT_OUTPUT_POSTSCRIPT):
        lgp_cmd = ["link-parser", dict_path, "-echo=1", "-postscript=1", "-graphics=0", verbosity,
                   "-limit=" + str(limit), "-timeout=" + str(timeout)]
    elif options & BIT_OUTPUT_CONST_TREE:
        lgp_cmd = ["link-parser", dict_path, "-echo=1", "-constituents=1", "-graphics=0", verbosity,
                   "-limit=" + str(limit), "-timeout=" + str(timeout)]
    else:
        lgp_cmd = ["link-parser", dict_path, "-echo=1", "-graphics=1", verbosity,
                   "-limit=" + str(limit), "-timeout=" + str(timeout)]

    if num_linkages > 1:
        lgp_cmd.append("-test=auto-next-linkage:" + str(num_linkages).strip())

    return lgp_cmd
