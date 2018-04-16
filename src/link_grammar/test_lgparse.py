import unittest
import sys
import  os
from link_grammar.lgparse import strip_token, parse_tokens, parse_links, calc_stat, parse_postscript, \
    parse_file_with_api, parse_file_with_lgp, \
    create_grammar_dir, LGParseError, BIT_STRIP, BIT_RWALL, BIT_CAPS, BIT_ULL_IN, BIT_OUTPUT_DIAGRAM, \
    BIT_OUTPUT_POSTSCRIPT, BIT_OUTPUT_CONST_TREE

class TestStringMethods(unittest.TestCase):
    """ TestStringMethods """
    postscript_str = "[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)][[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]"
    token_str = "(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)"
    link_str = "[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]"

    @staticmethod
    def cmp_lists(list1, list2) -> bool:
        if list1 is None or list2 is None or len(list1) != len(list2):
            return False

        for i in range(0, len(list1)):
            if list1[i] != list2[i]:
                return False

        return True

    def test_strip_token(self):
        """ test_strip_token """
        print(__doc__)

        self.assertEqual(strip_token("strange[!]"), "strange")
        self.assertEqual(strip_token("strange.a"), "strange")
        self.assertEqual(strip_token("[strange]"), "[strange]")

    def test_parse_tokens(self):
        """ test_parse_tokens """
        print(__doc__)

        options = 0

        # No RIGHT-WALL, no CAPS
        options |= BIT_STRIP
        tokens = parse_tokens(self.token_str, options)
        self.assertTrue(TestStringMethods.cmp_lists(tokens, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a',
                                                             'parent', 'before', '.']))

        # RIGHT-WALL and CAPS, no STRIP
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        tokens = parse_tokens(self.token_str, options)
        self.assertTrue(TestStringMethods.cmp_lists(tokens, ['###LEFT-WALL###', 'Dad[!]', 'was.v-d', 'not.e', 'a',
                                                             'parent.n', 'before', '.', '###RIGHT-WALL###']))

    def test_parse_links(self):
        """ test_parse_links """
        print(__doc__)

        links = parse_links(self.link_str, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.'])

        # [0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]
        self.assertTrue(TestStringMethods.cmp_lists(links, [ (0, '###LEFT-WALL###', 7, '.'),
                                                             (0, '###LEFT-WALL###', 1, 'dad'),
                                                             (1, 'dad', 2, 'was'),
                                                             (2, 'was', 5, 'parent'),
                                                             (2, 'was', 3, 'not'),
                                                             (4, 'a', 5, 'parent'),
                                                             (5, 'parent', 6, 'before') ]))

    def test_calc_stat(self):
        """ test_calc_stat """
        print(__doc__)

        f, n, s = calc_stat(['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.'])
        # print(f, n, s)
        self.assertTrue(f and (not n) and (s > 0.99))

        f, n, s = calc_stat(['[qqq]', '[www]', '[eee]', '[rrr]', '[ttt]', '[yyy]', '[uuu]', '[.]'])
        # print(f, n, s)
        self.assertTrue(n and (not f) and (s < 0.1))

        f, n, s = calc_stat(['###LEFT-WALL###', 'dad', 'was', 'not', '[a]', '[parent]', '[before]'])
        # print(f, n, s)
        self.assertTrue((not f) and (not n) and (s - 0.5 < 0.01))

    def test_parse_postscript(self):
        """ test_parse_postscript """
        print(__doc__)

        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        f, n, s = parse_postscript(TestStringMethods.postscript_str, options, sys.stdout)
        print("Completely: {}, Unparsed: {}, Average: {}".format(f, n, s))
        self.assertTrue(f==1 and n==0 and s-1.0 < 0.01)

    def test_parse_file_with_api(self):
        """ Test parse with default dictionary """
        print(__doc__)

        # Testing over poc-turtle corpus... 100% success is expected.
        options = 0 | BIT_STRIP
        f, n, s = parse_file_with_api("../../tests/test-data/dict/poc-turtle",
                             '../../tests/test-data/corpora/poc-turtle/poc-turtle.txt',
                             None, 1, options)
        # print("Completely: {0}, Unparsed: {1}, Average: {2}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

        # Testing over poc-turtle corpus retreaved from MST-parser links output. 100% success is expected.
        options = 0 | BIT_STRIP | BIT_ULL_IN
        f, n, s = parse_file_with_api("../../tests/test-data/dict/poc-turtle",
                             '../../tests/test-data/parses/poc-turtle-mst/poc-turtle-opencog-mst-parses.txt',
                             None, 1, options)
        # print("Completely: {0}, Unparsed: {1}, Average: {2}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

        # Testing over poc-english corpus retreaved from hand coded links
        f, n, s = parse_file_with_api("../../tests/test-data/dict/poc-turtle",
                             '../../tests/test-data/parses/poc-english-mst/poc_english_noamb_parse_ideal.txt',
                             None, 1, options)
        print("Completely: {0:2.2f}, Unparsed: {1:2.2f}, Average: {2:2.2f}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

    def test_parse_file_with_lgp(self):
        """ Test 'parse_file_with_lgp' with default dictionary """
        print(__doc__)

        # Testing over poc-turtle corpus... 100% success is expected.
        options = 0 | BIT_STRIP

        f, n, s = parse_file_with_lgp("../../tests/test-data/dict/poc-turtle",
                             '../../tests/test-data/corpora/poc-turtle/poc-turtle.txt',
                             None, 1, options)
        # print("Completely: {0}, Unparsed: {1}, Average: {2}".format(f, n, s))
        self.assertFalse(f+n+s < 0.001)
        self.assertTrue(f-1.0<0.01 and n<0.01 and s-1.0 < 0.01)

        # Test if two functions return the same results.
        tup_api = (.0, .0, .0)
        tup_lgp = (.0, .0, .0)

        tup_api = parse_file_with_api("../../tests/test-data/dict/poc-turtle",
                                      '../../tests/test-data/corpora/poc-turtle/poc-turtle.txt',
                                      None, 1, options)

        tup_lgp = parse_file_with_lgp("../../tests/test-data/dict/poc-turtle",
                                      '../../tests/test-data/corpora/poc-turtle/poc-turtle.txt',
                                      None, 1, options)

        print(tup_api)
        print(tup_lgp)

        self.assertEqual(tup_api, tup_lgp)

    def test_create_grammar_dir(self):
        self.assertTrue("en" == create_grammar_dir("en", "", "", 0))

        with self.assertRaises(LGParseError) as ctx:
            create_grammar_dir("/home/alex/en", "", "", 0)
        self.assertEqual("Dictionary path does not exist.", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()