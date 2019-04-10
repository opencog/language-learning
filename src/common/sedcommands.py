from .optconst import *

__all__ = ['get_sed_regex', 'get_sed_cmd_common_part']


def get_sed_regex(options: int) -> str:
    """
    Return regular expression built according to the set of specified options.

    :param options:     Grammar tester options.
    :return:            Regular expression string.
    """
    # If BIT_ULL_IN sed filters links leaving only sentences and removes square brackets around tokens if any.
    if options & BIT_ULL_IN:
        return r'/((^$)|(^([0-9]+[[:space:]]+.+){2}([[:space:]]+[-+0-9.e]+)?$))/d;s/\[([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*)\]/\1/g;s/.*/\L\0/g' \
            if options & BIT_INPUT_TO_LCASE \
            else r'/((^$)|(^([0-9]+[[:space:]]+.+){2}([[:space:]]+[-+0-9.e]+)?$))/d;s/\[([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*)\]/\1/g'

    # Otherwise sed removes only empty lines.
    else:
        return r"/^$/d;s/.*/\L\0/g" if options & BIT_INPUT_TO_LCASE else r"/^$/d"


def get_sed_cmd_common_part(options: int) -> list:
    """
    Return common part of sed invocation parammeter list used as an argument in Popen call.

    :param options:     Grammar tester options bit mask.
    :return:            List of sed arguments.
    """
    return ["sed", "-Ee", get_sed_regex(options)]

# grep -Pv '(?:^$)|(?:^\d+\s+.+\s+\d+(?:\s+.+){1,2}$)' pg27567.txt.ull | wc -l
#  sed -En '/(^$)|(^([0-9]+[[:space:]]+.+){2}$)/!p' pg27567.txt.ull | wc -l
#  sed -En '/(^$)|(^([0-9]+[[:space:]]+.+){2}([[:space:]]+[-+0-9.e]+)?$)/!p' pg27567.txt.ull | wc -l
#  sed -Ee '/((^$)|(^([0-9]+[[:space:]]+.+){2}([[:space:]]+[-+0-9.e]+)?$))/d;s/.*/\L&/g' pg27567.txt.ull | wc -l


# def get_sed_regex(options: int) -> str:
#
#     # If BIT_ULL_IN sed filters links leaving only sentences and removes square brackets around tokens if any.
#     if options & BIT_ULL_IN:
#         return r'/\(^[0-9].*$\)\|\(^$\)/d;s/\[\([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*\)\]/\1/g;s/.*/\L\0/g' \
#             if options & BIT_INPUT_TO_LCASE \
#             else r'/\(^[0-9].*$\)\|\(^$\)/d;s/\[\([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*\)\]/\1/g'
#
#     # Otherwise sed removes only empty lines.
#     else:
#         return r"/^$/d;s/.*/\L\0/g" if options & BIT_INPUT_TO_LCASE else r"/^$/d"
