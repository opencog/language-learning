import unittest
import sys
import os

from link_grammar.lgparse import calc_stat, parse_postscript, \
    parse_file_with_api, parse_file_with_lgp, parse_batch_ps_output, \
    create_grammar_dir, LGParseError, BIT_STRIP, BIT_RWALL, BIT_CAPS, BIT_ULL_IN, BIT_OUTPUT_DIAGRAM, \
    BIT_OUTPUT_POSTSCRIPT, BIT_OUTPUT_CONST_TREE, BIT_NO_LWALL

lg_post_output = """
echo set to 1
postscript set to 1
graphics set to 0
verbosity set to 0
tuna has fin .
[(LEFT-WALL)(tuna)(has)(fin)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

eagle isa bird .
[(LEFT-WALL)(eagle)(isa)(bird)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

fin isa extremity .
[(LEFT-WALL)(fin)(isa)(extremity)(.)]
[[0 1 0 (C05C04)][1 2 0 (C04C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

tuna isa fish .
[(LEFT-WALL)(tuna)(isa)(fish)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

fin has scale .
[(LEFT-WALL)(fin)([has])(scale)(.)]
[[0 1 0 (C05C04)][1 3 0 (C04C04)][3 4 0 (C04C03)]]
[0]

eagle has wing .
[(LEFT-WALL)(eagle)(has)(wing)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

wing has feather .
[(LEFT-WALL)(wing)([has])(feather)(.)]
[[0 1 0 (C05C04)][1 3 0 (C04C04)][3 4 0 (C04C03)]]
[0]

wing isa extremity .
[(LEFT-WALL)(wing)(isa)(extremity)(.)]
[[0 1 0 (C05C04)][1 2 0 (C04C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

herring isa fish .
[(LEFT-WALL)(herring)(isa)(fish)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

herring has fin .
[(LEFT-WALL)(herring)(has)(fin)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

parrot isa bird .
[(LEFT-WALL)(parrot)(isa)(bird)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

parrot has wing .
[(LEFT-WALL)(parrot)(has)(wing)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

Bye.
"""

class TestStringMethods(unittest.TestCase):
    """ TestStringMethods """

    @staticmethod
    def cmp_lists(list1, list2) -> bool:
        if list1 is None or list2 is None or len(list1) != len(list2):
            return False

        for i in range(0, len(list1)):
            if list1[i] != list2[i]:
                return False

        return True

    def test_calc_stat(self):
        """ test_calc_stat """
        print(__doc__, sys.stderr)

        f, n, s = calc_stat(['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.'])
        # print(f, n, s)
        self.assertTrue(f and (not n) and (s > 0.99))

        f, n, s = calc_stat(['[qqq]', '[www]', '[eee]', '[rrr]', '[ttt]', '[yyy]', '[uuu]', '[.]'])
        # print(f, n, s)
        self.assertTrue(n and (not f) and (s < 0.1))

        f, n, s = calc_stat(['###LEFT-WALL###', 'dad', 'was', 'not', '[a]', '[parent]', '[before]'])
        # print(f, n, s)
        self.assertTrue((not f) and (not n) and (s - 0.5 < 0.01))

    # @unittest.skip
    def test_parse_file_with_api(self):
        """ Test parse with default dictionary """
        print(__doc__, sys.stderr)

        # Testing over poc-turtle corpus... 100% success is expected.
        options = 0 | BIT_STRIP
        f, n, s = parse_file_with_api("test-data/dict/poc-turtle", "test-data/corpora/poc-turtle/poc-turtle.txt",
                             None, 1, options)
        # print("Completely: {0}, Unparsed: {1}, Average: {2}".format(f, n, s), file=sys.stderr)
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

        # Testing over poc-turtle corpus retreaved from MST-parser links output. 100% success is expected.
        options = 0 | BIT_STRIP | BIT_ULL_IN
        f, n, s = parse_file_with_api("test-data/dict/poc-turtle",
                             "test-data/parses/poc-turtle-mst/poc-turtle-opencog-mst-parses.txt",
                             None, 1, options)
        # print("Completely: {0}, Unparsed: {1}, Average: {2}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

        # Testing over poc-english corpus retreaved from hand coded links
        f, n, s = parse_file_with_api("test-data/dict/poc-turtle",
                             "test-data/parses/poc-english-mst/poc_english_noamb_parse_ideal.txt",
                             None, 1, options)
        # print("Completely: {0:2.2f}, Unparsed: {1:2.2f}, Average: {2:2.2f}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

    # @unittest.skip
    def test_parse_file_with_lgp(self):
        """ Test 'parse_file_with_lgp' with default dictionary """
        print(__doc__, sys.stderr)

        # Testing over poc-turtle corpus... 100% success is expected.
        options = 0 | BIT_STRIP

        f, n, s = parse_file_with_lgp("test-data/dict/poc-turtle", "test-data/corpora/poc-turtle/poc-turtle.txt",
                             None, 1, options)
        # print("Completely: {0}, Unparsed: {1}, Average: {2}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

        # Test if two functions return the same results.
        tup_api = (.0, .0, .0)
        tup_lgp = (.0, .0, .0)

        tup_api = parse_file_with_api("test-data/dict/poc-turtle", "test-data/corpora/poc-turtle/poc-turtle.txt",
                                      None, 1, options)

        tup_lgp = parse_file_with_lgp("test-data/dict/poc-turtle", "test-data/corpora/poc-turtle/poc-turtle.txt",
                                      None, 1, options)

        print(tup_api, sys.stderr)
        print(tup_lgp, sys.stderr)

        self.assertEqual(tup_api, tup_lgp)

    # @unittest.skip
    def test_create_grammar_dir(self):
        self.assertTrue("en" == create_grammar_dir("en", "", "", 0))

        with self.assertRaises(LGParseError) as ctx:
            create_grammar_dir("/home/alex/en", "", "", 0)
        self.assertEqual("Dictionary path does not exist.", str(ctx.exception))

    # @unittest.skip
    def test_parse_batch_ps_output(self):
        num_sent = len(parse_batch_ps_output(lg_post_output))
        self.assertEqual(num_sent, 12, "'parse_batch_ps_output()' returns '{}' instead of '{}'".format(num_sent, 12))


if __name__ == '__main__':
    unittest.main()