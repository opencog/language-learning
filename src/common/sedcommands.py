from .optconst import *

__all__ = ['get_sed_regex']

def get_sed_regex(options: int) -> str:

    # If BIT_ULL_IN sed filters links leaving only sentences and removes square brackets around tokens if any.
    if options & BIT_ULL_IN:
        return r'/\(^[0-9].*$\)\|\(^$\)/d;s/\[\([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*\)\]/\1/g;s/.*/\L\0/g' \
            if options & BIT_INPUT_TO_LCASE \
            else r'/\(^[0-9].*$\)\|\(^$\)/d;s/\[\([a-z0-9A-Z.,:\@"?!*~()\/\#\$&;^%_`\0xe2\x27\xE2\x80\x94©®°•…≤±×΅⁻¹²³€αβπγδμεθ«»=+-]*\)\]/\1/g'

    # Otherwise sed removes only empty lines.
    else:
        return r"/^$/d;s/.*/\L\0/g" if options & BIT_INPUT_TO_LCASE else r"/^$/d"
