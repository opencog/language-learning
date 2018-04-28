"""
    Statistics estimation set of functions
"""
def calc_stat(tokens:list) -> (int, int, float):
    """
    Calculate percentage of successfully linked tokens. Token in square brackets considered to be unlinked.

    :param tokens: List of tokens.
    :return: Tuple (int, int, float):
                - 1 if all tokens are linked, 0 otherwise;
                - 1 if all tokens are unlinked, 1 otherwise;
                - Percentage of successfully parsed tokens.
    """
    # Nothing to calculate if no tokens found
    if len(tokens) == 0:
        return 0.0

    total = 0

    # Initialize number of unlinked tokens
    unlinked = 0

    # We assume that all tokens included in square brackets are unlinked
    for token in tokens:
        # Exclude walls from statistics estimation
        if token.find("WALL") < 0:
            if token.startswith("["):
                unlinked += 1
            total += 1

    return unlinked == 0, total == unlinked, 1.0 if unlinked == 0 else 1.0 - float(unlinked) / float(total)


def calc_parse_quality(test_set:set, ref_set:set) -> (int, int, float):
    """
    Estimate parse quality

    :param test_set: Set of links being tested.
    :param ref_set: Refference set of links
    :return: Tuple (m, e, a) where  m - number of links missing in test set, e - number of extra links in test set,
                                    a - match links to total links ratio
    """
    len_ref = len(ref_set)

    if len_ref > 0:
        return len(ref_set - test_set), len(test_set - ref_set), float(len(test_set & ref_set)) / float(len_ref)

    return 0, 0, 0.0
