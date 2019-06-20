
__all__ = [
    'BIT_CAPS', 'BIT_RWALL', 'BIT_STRIP', 'BIT_OUTPUT', 'BIT_ULL_IN', 'BIT_RM_DIR',
    'BIT_OUTPUT_DIAGRAM', 'BIT_OUTPUT_POSTSCRIPT', 'BIT_OUTPUT_CONST_TREE', 'BIT_OUTPUT_ALL',
    'BIT_LG_GR_NAME', 'BIT_DPATH_CREATE', 'BIT_LG_EXE', 'BIT_NO_LWALL', 'BIT_SEP_STAT', 'BIT_LOC_LANG',
    'BIT_PARSE_QUALITY', 'BIT_NO_PERIOD', 'BIT_ULL_NO_LWALL', 'BIT_GRSUBDIR_CREATE', 'BIT_INPUT_TO_LCASE',
    'BIT_EXISTING_DICT', 'BIT_EXCLUDE_TIMEOUTED', 'BIT_EXCLUDE_PANICED', 'BIT_EXCLUDE_EXPLOSION',
    'BIT_FILTER_DIR_SPEECH', 'BIT_STRICT_TOKENIZATION', 'BIT_IGNORE_SENT_MISMATCH', 'get_options'
]

# Link Grammar output format constants. If no bits set, ULL defacto format is used.
BIT_OUTPUT_DIAGRAM      = 0b0001
BIT_OUTPUT_POSTSCRIPT   = 0b0010
BIT_OUTPUT_CONST_TREE   = 0b0100
BIT_OUTPUT_ALL = BIT_OUTPUT_DIAGRAM | BIT_OUTPUT_POSTSCRIPT | BIT_OUTPUT_CONST_TREE
BIT_OUTPUT = BIT_OUTPUT_ALL

BIT_CAPS                = (1<<3)            # Preserve capitalized letters in tokens
BIT_RWALL               = (1<<4)            # Keep RIGHT-WALL tokens and the links
BIT_STRIP               = (1<<5)            # Strip off token suffixes
BIT_ULL_IN              = (1<<6)            # If set, parse_file_with_api() is informed that ULL parses are used
                                            # as input, so only sentences should be parsed, links should be
                                            # filtered out.
BIT_RM_DIR              = (1<<7)            # Remove grammar dictionary if it already exists. Then recreate it
                                            # from scratch.
BIT_LG_GR_NAME          = (1<<8)            # Treat dictionary path argument as Link Grammar dictionary path
BIT_DPATH_CREATE        = (1<<9)            # Recreate dictionary path instead of source path
BIT_LG_EXE              = (1<<10)           # Use link-parser executable in a separate process for parsing
BIT_NO_LWALL            = (1<<11)           # Exclude left-wall from statistics estimation and ULL output
BIT_NO_PERIOD           = (1<<12)           # Exclude period from statistics estimation
BIT_SEP_STAT            = (1<<13)           # Generate separate statistics for each corpus file
BIT_LOC_LANG            = (1<<14)           # Keep language grammar directory localy in output directory
BIT_PARSE_QUALITY       = (1<<15)           # Compare links of .ull file and reference file for parse quality estimation
BIT_ULL_NO_LWALL        = (1<<16)           # Exclude LEFT-WALL from ULL output
BIT_GRSUBDIR_CREATE     = (1<<17)           # Create subdirectories named after each grammar file if grammar directory
                                            #   has multiple .dict files in it.
BIT_INPUT_TO_LCASE      = (1<<18)           # Convert input stream characters to lower case
BIT_EXISTING_DICT       = (1<<19)           # Dictionary path should be treated as path to proper Link Grammar dictionary
BIT_EXCLUDE_TIMEOUTED   = (1<<20)           # Exclude linkage(s) from statistics estimations if LG timeout is expired
BIT_EXCLUDE_PANICED     = (1<<21)           # Exclude linkage(s) from statistics estimation if LG 'panic' is detected
BIT_EXCLUDE_EXPLOSION   = (1<<22)           # Exclude linkage(s) from statistics estimation if LG combinatorial
                                            #   explosion is detected.
BIT_FILTER_DIR_SPEECH   = (1<<23)           # Filter out direct speech.
BIT_STRICT_TOKENIZATION = (1<<24)           # Ignore tokenization discrepancies when comparing parses
BIT_IGNORE_SENT_MISMATCH= (1<<25)           # Ignore sentences mismatch when comparing parses

config_options = {
    "keep_caps": (BIT_CAPS, False),
    "keep_rwall": (BIT_RWALL, False),
    "strip_suffix": (BIT_STRIP, True),
    "ull_input": (BIT_ULL_IN, False),
    "rm_grammar_dir": (BIT_RM_DIR, False),
    "dup_dict_path": (BIT_DPATH_CREATE, False),
    "use_link_parser": (BIT_LG_EXE, True),
    "ignore_left_wall": (BIT_NO_LWALL, True),
    "ignore_period": (BIT_NO_PERIOD, True),
    "separate_stat": (BIT_SEP_STAT, False),
    "store_dict_localy": (BIT_LOC_LANG, False),
    "calc_parse_quality": (BIT_PARSE_QUALITY, False),
    "no_left_wall_in_ull": (BIT_ULL_NO_LWALL, False),
    "lg_grammar_name": (BIT_LG_GR_NAME, False),
    "input_to_lcase": (BIT_INPUT_TO_LCASE, False),
    "existing_dict_dir": (BIT_EXISTING_DICT, False),
    "exclude_timeouted": (BIT_EXCLUDE_TIMEOUTED, False),
    "exclude_paniced": (BIT_EXCLUDE_PANICED, False),
    "exclude_explosion": (BIT_EXCLUDE_EXPLOSION, False),
    "strict_tokenization": (BIT_STRICT_TOKENIZATION, False),
    "ignore_sentence_mismatch": (BIT_IGNORE_SENT_MISMATCH, False)
}

output_format = {
    "diagram": BIT_OUTPUT_DIAGRAM,
    "postscript": BIT_OUTPUT_POSTSCRIPT,
    "constituent": BIT_OUTPUT_CONST_TREE
}

def get_options(cfg_options: dict) -> int:
    opts = 0

    # Set default values
    for opt in config_options:
        if opt[1] == True:
            opts |= opt[0]

    # Set configuration dictionary values
    for opt in cfg_options:

        if opt in config_options and cfg_options[opt] == True:
            opts |= config_options[opt][0]

        if opt == "parse_format":
            frm = cfg_options[opt]

            if frm in output_format:
                opts |= output_format[frm]

    return opts
