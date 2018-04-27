import unittest
import sys

try:
    from link_grammar.psparse import strip_token, parse_tokens, parse_links, parse_postscript
    from link_grammar.optconst import *

except ImportError:
    from psparse import strip_token, parse_tokens, parse_links, parse_postscript
    from optconst import *


class TestPSParse(unittest.TestCase):

    post_all_walls = "[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)][[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]"
    post_no_walls = "[(eagle)(has)(wing)(.)][[0 2 1 (C04C01)][1 2 0 (C01C01)][2 3 0 (C01C05)]][0]"
    post_no_links = "[([herring])([isa])([fish])([.])][][0]"

    link_str = "[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]"

    tokens_all_walls = "(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)"
    tokens_no_walls = "(eagle)(has)(wing)(.)"

    @staticmethod
    def cmp_lists(list1:[], list2:[]) -> bool:
        if list1 is None or list2 is None or len(list1) != len(list2):
            return False

        for i in range(0, len(list1)):
            if list1[i] != list2[i]:
                return False

        return True

    def test_strip_token(self):
        """ test_strip_token """
        print(__doc__, sys.stderr)

        self.assertEqual(strip_token("strange[!]"), "strange")
        self.assertEqual(strip_token("strange.a"), "strange")
        self.assertEqual(strip_token("[strange]"), "[strange]")

    def test_parse_tokens(self):
        """ test_parse_tokens """
        print(__doc__, sys.stderr)

        options = 0

        # No RIGHT-WALL, no CAPS
        options |= BIT_STRIP
        tokens = parse_tokens(self.tokens_all_walls, options)
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a',
                                                 'parent', 'before', '.']))

        # Tokens without walls
        tokens = parse_tokens(self.tokens_no_walls, options)
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing', '.']))

        # RIGHT-WALL and CAPS, no STRIP
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        tokens = parse_tokens(self.tokens_all_walls, options)
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'Dad[!]', 'was.v-d', 'not.e', 'a',
                                                 'parent.n', 'before', '.', '###RIGHT-WALL###']))

        # Tokens without walls
        tokens = parse_tokens(self.tokens_no_walls, options)
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing', '.']))

        # NO_LWALL and CAPS, no STRIP
        options |= (BIT_NO_LWALL | BIT_CAPS)
        options &= (~(BIT_STRIP | BIT_RWALL))
        tokens = parse_tokens(self.tokens_all_walls, options)
        self.assertTrue(self.cmp_lists(tokens, ['Dad[!]', 'was.v-d', 'not.e', 'a',
                                                 'parent.n', 'before', '.']))

    def test_parse_links(self):
        """ test_parse_links """
        print(__doc__, sys.stderr)

        links = parse_links(self.link_str, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.'])

        # [0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]
        self.assertTrue(self.cmp_lists(links, [  (0, '###LEFT-WALL###', 7, '.'),
                                                 (0, '###LEFT-WALL###', 1, 'dad'),
                                                 (1, 'dad', 2, 'was'),
                                                 (2, 'was', 5, 'parent'),
                                                 (2, 'was', 3, 'not'),
                                                 (4, 'a', 5, 'parent'),
                                                 (5, 'parent', 6, 'before') ]))

    @unittest.skip
    def test_parse_postscript(self):
        """ test_parse_postscript """
        print(__doc__, sys.stderr)

        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        f, n, s = parse_postscript(self.post_all_walls, options, sys.stdout)
        print("Completely: {}, Unparsed: {}, Average: {}".format(f, n, s))
        self.assertTrue(f==1 and n==0 and s-1.0 < 0.01)

        f, n, s = parse_postscript(self.post_no_walls, options, sys.stdout)
        print("Completely: {}, Unparsed: {}, Average: {}".format(f, n, s))
        self.assertTrue(f==1 and n==0 and s-1.0 < 0.01)

        f, n, s = parse_postscript(self.post_no_links, options, sys.stdout)
        print("Completely: {}, Unparsed: {}, Average: {}".format(f, n, s))
        self.assertTrue(f==0 and n==1 and s < 0.01)


if __name__ == '__main__':
    unittest.main()
