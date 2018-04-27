import unittest

try:
    from link_grammar.parsestat import calc_parse_quality, calc_stat

except ImportError:
    from parsestat import calc_parse_quality, calc_stat


# Token indexes
LWALL = 0; tuna = 1; isa = 2; fish = 3; DOT = 4; RWALL = 5

# Reference set
ref_set =   {(LWALL, DOT), (LWALL, isa), (LWALL, tuna), (tuna, isa), (isa, fish), (fish, DOT)}

# Equal set (0, 0, 1.0)
test_set1 = {(LWALL, DOT), (LWALL, isa), (LWALL, tuna), (tuna, isa), (isa, fish), (fish, DOT)}

# Three link missing set (3, 0, 0.5)
test_set2 = {(LWALL, DOT), (LWALL, isa), (LWALL, tuna)}

# One extra link (0, 1, 1.0)
test_set3 = {(LWALL, DOT), (LWALL, isa), (LWALL, tuna), (tuna, isa), (isa, fish), (fish, DOT), (DOT, RWALL)}

# Three different links (3, 3, 0.5)
test_set4 = {(LWALL, DOT), (LWALL, fish), (LWALL, tuna), (tuna, DOT), (isa, fish), (isa, DOT)}


class TestStat(unittest.TestCase):

    def test_calc_parse_quality_equal(self):
        """ Equal set test """
        (m, e, q) = calc_parse_quality(test_set1, ref_set)

        self.assertEqual((0, 0, 1.0), (m, e, q))

    def test_calc_parse_quality_three_missing(self):
        """ Three missing links test """
        (m, e, q) = calc_parse_quality(test_set2, ref_set)

        self.assertEqual((3, 0, 0.5), (m, e, q))

    def test_calc_parse_quality_one_extra(self):
        """ One extra link test """
        (m, e, q) = calc_parse_quality(test_set3, ref_set)

        self.assertEqual((0, 1, 1.0), (m, e, q))

    def test_calc_parse_quality_three_different(self):
        """ Three different links test """
        (m, e, q) = calc_parse_quality(test_set4, ref_set)

        self.assertEqual((3, 3, 0.5), (m, e, q))

if __name__ == '__main__':
    unittest.main()
