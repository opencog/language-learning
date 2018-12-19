from typing import List
from .optconst import *


def get_sed_regex(options: int) -> str:

    # If BIT_ULL_IN sed filters links leaving only sentences and removes square brackets around tokens if any.
    if options & BIT_ULL_IN:
        return r'/\(^[0-9].*$\)\|\(^$\)/d;s/\[\([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*\)\]/\1/g;s/.*/\L\0/g' \
            if options & BIT_INPUT_TO_LCASE \
            else r'/\(^[0-9].*$\)\|\(^$\)/d;s/\[\([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*\)\]/\1/g'

    # Otherwise sed removes only empty lines.
    else:
        return r"/^$/d;s/.*/\L\0/g" if options & BIT_INPUT_TO_LCASE else r"/^$/d"


def get_linkparser_command(options: int, dict_path: str, limit: int, timeout: int, verb: int=1) -> List[str]:

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

    return lgp_cmd
