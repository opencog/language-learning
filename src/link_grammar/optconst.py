
__all__ = [
    # 'LG_DICT_PATH',
    'BIT_CAPS', 'BIT_RWALL', 'BIT_STRIP', 'BIT_OUTPUT', 'BIT_ULL_IN', 'BIT_RM_DIR',
    'BIT_OUTPUT_DIAGRAM', 'BIT_OUTPUT_POSTSCRIPT', 'BIT_OUTPUT_CONST_TREE', 'BIT_OUTPUT_ALL',
    'BIT_BEST_LINKAGE', 'BIT_DPATH_CREATE', 'BIT_LG_EXE', 'BIT_NO_LWALL', 'BIT_SEP_STAT', 'BIT_LOC_LANG'
]

# Output format constants. If no bits set, ULL defacto format is used.
BIT_OUTPUT_DIAGRAM      = 0b0001
BIT_OUTPUT_POSTSCRIPT   = 0b0010
BIT_OUTPUT_CONST_TREE   = 0b0100
BIT_OUTPUT_ALL = BIT_OUTPUT_DIAGRAM | BIT_OUTPUT_POSTSCRIPT | BIT_OUTPUT_CONST_TREE
BIT_OUTPUT = BIT_OUTPUT_ALL

BIT_CAPS                = (1<<3)            # Keep capitalized letters in tokens
BIT_RWALL               = (1<<4)            # Keep RIGHT-WALL tokens and the links
BIT_STRIP               = (1<<5)            # Strip off token suffixes
BIT_ULL_IN              = (1<<6)            # If set, parse_file_with_api() is informed that ULL parses are used
                                            # as input, so only sentences should be parsed, links should be
                                            # filtered out.
BIT_RM_DIR              = (1<<7)            # Remove grammar dictionary if it already exists. Then recreate it
                                            # from scratch.
BIT_BEST_LINKAGE        = (1<<8)            # Take most probable linkage.
BIT_DPATH_CREATE        = (1<<9)            # Recreate dictionary path instead of source path
BIT_LG_EXE              = (1<<10)           # Use link-parser executable in a separate process for parsing
BIT_NO_LWALL            = (1<<11)           # Exclude left-wall from statistics estimation and ULL output
BIT_SEP_STAT            = (1<<12)           # Generate separate statistics for each corpus file
BIT_LOC_LANG            = (1<<13)           # Keep language grammar directory localy in output directory
