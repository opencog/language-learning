import unittest
import sys

from src.grammar_tester.psparse import strip_token, parse_tokens, parse_links, parse_postscript, get_link_set, \
    prepare_tokens, skip_command_response, skip_linkage_header, PS_TIMEOUT_EXPIRED, PS_PANIC_DETECTED
from src.grammar_tester.optconst import *
from src.grammar_tester.parsestat import parse_metrics


gutenberg_children_bug = \
"""
[(LEFT-WALL)(")(project.v)(gutenberg[?].n)('s.p)(alice[?].n)('s.p)(adventures.n)([in])(wonderland.n)
(,)(by)(lewis[!])(carroll[?].n)(")(()(edited.v-d)())]
[[0 2 1 (Wi)][0 1 0 (ZZZ)][2 9 2 (Os)][6 9 1 (Ds**x)][5 6 0 (YS)][4 5 0 (D*u)][3 4 0 (YS)]
[7 9 0 (AN)][9 11 1 (MXsx)][10 11 0 (Xd)][11 17 2 (Xc)][11 13 1 (Jp)][12 13 0 (AN)][13 16 1 (MXsp)]
[16 17 0 (Xca)][13 14 0 (ZZZ)][15 16 0 (Xd)]]
[0]
"""
gutenberg_children_bug2 = "[ebook # @number@ ][(LEFT-WALL)(release.n)(date.n)(:.j)(@date@[?].n)([)(ebook[?].a)([#])" \
                          "(@number@[?].n)(])][[0 3 2 (Xx)][0 2 1 (Wa)][1 2 0 (AN)][3 4 0 (Jp)][4 8 2 (MXs)]" \
                          "[5 8 1 (Xd)][6 8 0 (A)][8 9 0 (Xc)]][0]"


# cleaned_Gutenberg_Children bug list
cgch_bug_001 = \
"""
[ illustration : " i tell you what , you stay right here ! "[(LEFT-WALL)([[])(illustration.n-u)(:.v)(")([i])(tell.v)(you)(what)(,)(you)(stay.v)(right.a)(here)(!)(")][[0 14 4 (Xp)][0 9 3 (Xx)][0 6 2 (WV)][0 2 0 (Wd)][2 3 0 (Ss)][3 6 1 (I*v)][3 4 0 (ZZZ)][6 8 1 (QI)][6 7 0 (Ox)][9 11 1 (WV)][9 10 0 (Wd)][10 11 0 (Sp)][11 12 0 (Pa)][12 13 0 (MVp)][14 15 0 (ZZZ)]][0]
"""
# most people start at our web site which has the main pg search facility:
alice_bug_001 = \
"""
[(most)(people)(start)(at)([our])(web)(site)([which])([has])([the])
([main])([pg])([search])([facility:])]
[[0 1 0 (C26C33)][1 2 0 (C33C54)][2 3 0 (C54C22)][3 6 1 (C22C17)][5 6 0 (C23C17)]]
[0]
"""

# its business office is located at @number@ north @number@ west, salt lake city, ut @number@ , ( @number@ ) @number@ - @number@ , email business@pglaf.org.
alice_bug_002 = \
"""
[(LEFT-WALL)(its)(business.n-u)(office.n)(is.v)(located.v-d)(at)(@number@[?].n)(north.a)(@number@[?].a)
(west.a)(,)(salt.n-u)(lake.n)(city.n)(,)(ut[?].v)(@number@[?].a)(,)([(])
(@number@[?].a)())(@number@[?].a)(-.r)(@number@[?].a)(,)(email.s)(business@pglaf.org[?].n)(.)]
[[0 28 6 (Xp)][0 16 5 (WV)][0 11 4 (Xx)][0 5 3 (WV)][0 3 2 (Wd)][1 3 1 (Ds**x)][2 3 0 (AN)]
[3 4 0 (Ss*s)][4 5 0 (Pv)][5 9 1 (Pa)][5 6 0 (MVp)][6 7 0 (Jp)][7 8 0 (Mp)][9 10 0 (MVp)]
[11 15 3 (Xx)][15 16 0 (Wa)][11 14 2 (Wa)][12 14 1 (AN)][13 14 0 (AN)][16 27 5 (Os)][26 27 0 (AN)]
[17 26 4 (A)][17 18 0 (Xc)][20 26 3 (A)][20 21 0 (Xc)][22 26 2 (A)][22 23 0 (Xc)][24 26 1 (A)]
[24 25 0 (Xc)]]
[0]
"""

alice_bug_003 = \
"""
[(LEFT-WALL)([(])(alice[?].n)(had.v-d)(no.misc-d)(idea.n)(what)(latitude.n-u)(was.v-d)(,)
(or.ij)(longitude.n-u)(either.r)(,)([but])(thought.q-d)(they)(were.v-d)(nice.a)(grand.a)
(words.n)(to.r)(say.v)(.)([)])]
[[0 23 5 (Xp)][0 10 3 (Xx)][0 3 1 (WV)][0 2 0 (Wd)][2 3 0 (Ss)][3 5 1 (Os)][4 5 0 (Ds**x)]
[5 6 0 (MXs)][6 9 2 (Xca)][9 10 0 (Xd)][6 8 1 (Bsdt)][6 7 0 (Rn)][7 8 0 (Ss)][10 17 4 (WV)]
[10 11 0 (Wdc)][11 17 3 (Ss)][12 17 2 (E)][15 17 1 (Eq)][13 15 0 (Xd)][15 16 0 (SIpj)][17 20 2 (Opt)]
[18 20 1 (A)][19 20 0 (A)][20 22 1 (Bpw)][20 21 0 (R)][21 22 0 (I)]]
[0]
"""

alice_bug_004 = \
"""
[(LEFT-WALL)(posting.g)(date.n)(:.j)(@date@[?].a)([)(ebook[?].a)([#])(@number@[?].n)(])
(release.n)(date.n)(:.j)([@date@])(last.ord)(updated.v-d)(:.v)(@date@[?].n)]
[[0 3 2 (Xx)][0 2 1 (Wa)][1 2 0 (AN)][3 12 5 (Xx)][3 11 4 (Wa)][10 11 0 (AN)][4 10 3 (A)]
[4 8 2 (MX*ta)][5 8 1 (Xd)][6 8 0 (A)][8 9 0 (Xc)][12 16 2 (WV)][12 14 0 (Wd)][14 16 1 (Ss*o)]
[14 15 0 (Mv)][16 17 0 (Ost)]]
[0]
"""

gutenberg_children_bug_002 = \
"""
[(LEFT-WALL)([a])(millennium.n-u)(fulcrum.n)(edition.n)([(])([c])([)])(1991[!])([by])
(duncan[?].n)(research.n-u)]
[[0 11 5 (Wa)][2 11 4 (AN)][3 11 3 (AN)][4 11 2 (AN)][8 11 1 (AN)][10 11 0 (AN)]]
[0]
"""

gutenberg_children_bug_002t = "[(LEFT-WALL)([a])(millennium.n-u)(fulcrum.n)(edition.n)([(])([c])([)])(1991[!])([by])" \
                              "(duncan[?].n)(research.n-u)]"

gutenberg_children_bug_002tr = [r"###LEFT-WALL###", "[a]", "millennium", "fulcrum", "edition", "[(]", "[c]", "[)]",
                                "1991", "[by]", "duncan", "research"]

gutenberg_children_bug_002l = "[[0 11 5 (Wa)][2 11 4 (AN)][3 11 3 (AN)][4 11 2 (AN)][8 11 1 (AN)][10 11 0 (AN)]][0]"

gutenberg_children_bug_002lr = [(0, 11), (2, 11), (3, 11), (4, 11), (8, 11), (10, 11)]

explosion_bug = \
"""
conclusions : icp-sf-ms is a reliable method of blood analysis for cd , mn and pb even for the evaluation on an individual basis.
by comparing eyebrow shape and position in both young and mature women , this study provides objective data with which to plan forehead rejuvenating procedures.
the odds of being overweight in adulthood was @number@ times greater ( @percent@ ci : @date@ @number@ ) in overweight compared with healthy weight youth.
holocaust survivors did not differ in the level of resilience from comparisons ( mean : @number@ ± @number@ vs. @number@ ± @number@ respectively ) .
[(LEFT-WALL)(holocaust.n)(survivors.n)(did.v-d)(not.e)(differ.v)(in.r)(the)(level.n)(of)
(resilience.n-u)(from)(comparisons.n)(()(mean.a)([:])(@number@[?].n)(±[?].n)(@number@[?].n)(vs.)
(@number@[?].n)(±[?].n)(@number@[?].n)([respectively])())(.)]
[[0 25 4 (Xp)][0 5 2 (WV)][0 2 1 (Wd)][1 2 0 (AN)][2 3 0 (Sp)][3 5 1 (I*d)][3 4 0 (N)]
[4 5 0 (En)][5 11 2 (MVp)][5 6 0 (MVp)][6 8 1 (Js)][7 8 0 (Ds**c)][8 9 0 (Mf)][9 10 0 (Jp)]
[10 11 0 (Mp)][11 12 0 (Jp)][12 18 3 (MXp)][13 18 2 (Xd)][14 18 1 (A)][17 18 0 (AN)][16 17 0 (AN)]
[18 24 3 (Xc)][18 19 0 (Mp)][19 22 2 (Jp)][20 22 1 (AN)][21 22 0 (AN)]]
[0]
"""

timeout_linkage = \
"""
No complete linkages found.
Timer is expired!
Entering "panic" mode...
Found 576744359 linkages (100 of 100 random linkages had no P.P. violations) at null count 4
	Linkage 1, cost vector = (UNUSED=4 DIS= 0.00 LEN=19)
[(but)([I])(have)(passed)(my)(royal)(word)([,])(and)([I])
(cannot)(break)(it)([,])(so)(there)(is)(no)(help)(for)
(you)(..y)(')]
[[0 5 1 (FK)][0 2 0 (FF)][2 3 0 (FC)][3 4 0 (CJ)][5 10 1 (KG)][5 6 0 (KH)][8 10 0 (BG)]
[10 12 1 (GE)][11 12 0 (CE)][12 14 0 (EF)][14 20 2 (FF)][18 20 1 (CF)][17 18 0 (JC)][16 17 0 (LJ)]
[15 16 0 (EL)][18 19 0 (CB)][20 22 1 (FC)][21 22 0 (CC)]]
[0]
"""


class TestPSParse(unittest.TestCase):

    post_all_walls = "[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)]" \
                     "[[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)]" \
                     "[4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]"
    post_no_walls = "[(eagle)(has)(wing)(.)][[0 2 1 (C04C01)][1 2 0 (C01C01)][2 3 0 (C01C05)]][0]"
    post_no_links = "[([herring])([isa])([fish])([.])][][0]"

    link_str = "[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]"

    tokens_all_walls = "(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)"
    tokens_no_walls = "(eagle)(has)(wing)(.)"
    tokens_no_walls_no_period = "(eagle)(has)(wing)"

    def test_new_tokenizer(self):

        def find_end_of_token(text, pos: int) -> int:

            # Assume the open brace is already skipped
            braces = 1
            brackets = 0

            text_len = len(text)

            while pos < text_len:

                current = text[pos]

                if current == r"(":
                    # If not "[(]"
                    if not brackets:
                        braces += 1

                elif current == r")":
                    # if not "[)]"
                    if not brackets:
                        braces -= 1

                    if not braces:
                        return pos

                elif current == r"[":
                    brackets += 1

                elif current == r"]":
                    brackets -= 1

                pos += 1

            return pos

        def tokenizer(text: str) -> list:
            tokens = []
            pos = 0
            old = -1

            while pos < len(text):
                if pos == old:
                    print("Infinite loop detected...")
                    break

                # To avoid infinite loop in case of errors in postscript string
                old = pos

                if text[pos] == r"(":
                    pos += 1

                end = find_end_of_token(text, pos)

                if end > pos:
                    tokens.append(text[pos:end])

                pos = end + 1

            return tokens

        self.assertEqual(["eagle", "has", "wing", "."], tokenizer("(eagle)(has)(wing)(.)"))

        self.assertEqual(["LEFT-WALL", "Dad[!]", "was.v-d", "not.e", "a", "parent.n", "before", ".", "RIGHT-WALL"],
                         tokenizer("(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)"))

        post = "(LEFT-WALL)([(])(alice[?].n)(had.v-d)(no.misc-d)(idea.n)(what)(latitude.n-u)(was.v-d)(,)(or.ij)" \
               "(longitude.n-u)(either.r)(,)([but])(thought.q-d)(they)(were.v-d)(nice.a)(grand.a)(words.n)(to.r)(say.v)" \
               "(.)([)])"
        ref = ["LEFT-WALL", "[(]", "alice[?].n", "had.v-d", "no.misc-d", "idea.n", "what", "latitude.n-u", "was.v-d",
               ",", "or.ij", "longitude.n-u", "either.r", ",", "[but]", "thought.q-d", "they", "were.v-d", "nice.a",
               "grand.a", "words.n", "to.r", "say.v", ".", "[)]"]

        # print(tokenizer(post))

        self.assertEqual(ref, tokenizer(post))

    @staticmethod
    def cmp_lists(list1: [], list2: []) -> bool:
        if list1 is None or list2 is None or len(list1) != len(list2):
            return False

        for i in range(0, len(list1)):
            if list1[i] != list2[i]:
                return False

        return True

    def test_strip_token(self):
        """ Test for stripping Link Grammar suffixes off tokens """
        self.assertEqual(strip_token("strange[!]"), "strange")
        self.assertEqual(strip_token("strange.a"), "strange")
        self.assertEqual(strip_token("[strange]"), "[strange]")

    # @unittest.skip
    def test_parse_tokens_alice_003(self):
        """ Test for proper parsing of '[(]' revealed by Alice in Wonderland corpus """
        options = BIT_STRIP | BIT_NO_LWALL | BIT_NO_PERIOD

        # sent = "(alice had no idea what latitude was, or longitude either, but thought they were nice grand words to say.)"
        post = "(LEFT-WALL)([(])(alice[?].n)(had.v-d)(no.misc-d)(idea.n)(what)(latitude.n-u)(was.v-d)(,)(or.ij)" \
               "(longitude.n-u)(either.r)(,)([but])(thought.q-d)(they)(were.v-d)(nice.a)(grand.a)(words.n)(to.r)(say.v)" \
               "(.)([)])"
        ref = \
        ["###LEFT-WALL###", "[(]", "alice", "had", "no", "idea", "what", "latitude", "was", ",", "or", "longitude",
        "either", ",", "[but]", "thought", "they", "were", "nice", "grand", "words", "to", "say", ".", "[)]"]

        tokens = parse_tokens(post, options)[0]
        self.assertEqual(ref, tokens)

    # @unittest.skip
    def test_parse_tokens_alice_004(self):
        """ Test for proper parsing of square brackets revealed by Alice in Wonderland corpus """
        options = BIT_STRIP | BIT_NO_LWALL | BIT_NO_PERIOD

        post = "(LEFT-WALL)(posting.g)(date.n)(:.j)(@date@[?].a)([)(ebook[?].a)([#])(@number@[?].n)(])(release.n)" \
               "(date.n)(:.j)([@date@])(last.ord)(updated.v-d)(:.v)(@date@[?].n)"

        ref = ["###LEFT-WALL###", "posting", "date", ":", "@date@", "[", "ebook", "[#]", "@number@", "]", "release",
               "date", ":", "[@date@]", "last", "updated", ":", "@date@"]

        tokens = parse_tokens(post, options)[0]
        self.assertEqual(ref, tokens)

    # @unittest.skip
    def test_parse_tokens(self):
        """ test_parse_tokens """

        options = 0

        # No RIGHT-WALL, no CAPS
        options |= BIT_STRIP
        # tokens = parse_tokens(self.tokens_all_walls, options)
        # self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a',
        #                                         'parent', 'before', '.']))

        # Tokens without walls
        tokens = parse_tokens(self.tokens_no_walls, options)[0]
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing', '.']))

        # RIGHT-WALL and CAPS, no STRIP
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        tokens = parse_tokens(self.tokens_all_walls, options)[0]
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'Dad[!]', 'was.v-d', 'not.e', 'a',
                                                'parent.n', 'before', '.', '###RIGHT-WALL###']))

        # Tokens without walls
        tokens = parse_tokens(self.tokens_no_walls, options)[0]
        # print(tokens, file=sys.stdout)
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing', '.']))

    @unittest.skip
    def test_parse_tokens_no_left_wall(self):
        # NO_LWALL and CAPS, no STRIP
        options = 0
        options |= BIT_CAPS | BIT_NO_LWALL
        # options |= (BIT_NO_LWALL | BIT_CAPS)
        # options &= (~(BIT_STRIP | BIT_RWALL))
        tokens = parse_tokens(self.tokens_all_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['Dad[!]', 'was.v-d', 'not.e', 'a',
                                                'parent.n', 'before', '.']))

    @unittest.skip
    def test_parse_tokens_no_walls_no_period(self):
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_NO_LWALL
        tokens = parse_tokens(self.tokens_all_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['dad', 'was', 'not', 'a', 'parent', 'before']))

    @unittest.skip
    def test_parse_tokens_rwall_no_period(self):
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_RWALL
        tokens = parse_tokens(self.tokens_all_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before',
                                                '###RIGHT-WALL###']))

    @unittest.skip
    def test_parse_tokens_no_period(self):
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_RWALL
        tokens = parse_tokens(self.tokens_no_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing']))

    # @unittest.skip
    def test_parse_no_period_if_no_period(self):
        """ Test for parsing sentence with no walls and period """
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_RWALL
        tokens = parse_tokens(self.tokens_no_walls_no_period, options)[0]

        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing']))

    # @unittest.skip
    def test_parse_links(self):
        """ Test for parsing links out when LW and period are presented """
        links = parse_links(self.link_str, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.'], 0)

        # [0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]
        self.assertTrue(self.cmp_lists(links, [  (0, 7),
                                                 (0, 1),
                                                 (1, 2),
                                                 (2, 5),
                                                 (2, 3),
                                                 (4, 5),
                                                 (5, 6) ]))

    # @unittest.skip
    def test_parse_postscript_all_walls(self):
        """ Test for parsing postscript with both walls in """
        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        tokens, links = parse_postscript(self.post_all_walls, options, sys.stdout)
        pm = parse_metrics(tokens)
        self.assertEqual(1.0, pm.completely_parsed_ratio)
        self.assertEqual(0.0, pm.completely_unparsed_ratio)
        self.assertEqual(1.0, pm.average_parsed_ratio)

    # @unittest.skip
    def test_parse_postscript_no_walls(self):
        """ Test for parsing_postscript with no walls in """
        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(self.post_no_walls, options, sys.stdout)
        pm = parse_metrics(tokens)
        self.assertEqual(1.0, pm.completely_parsed_ratio)
        self.assertEqual(0.0, pm.completely_unparsed_ratio)
        self.assertEqual(1.0, pm.average_parsed_ratio)

    # @unittest.skip
    def test_parse_postscript_no_links(self):
        """ Test for parsing postscript with no links """
        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(self.post_no_links, options, sys.stdout)
        self.assertEqual(0, len(links))

    # @unittest.skip
    def test_parse_postscript_gutenchildren_bug(self):
        """ Test for number of tokens (bug from Gutenberg Children corpus) """
        options = 0
        # options |= (BIT_RWALL | BIT_CAPS)
        # options &= ~BIT_STRIP

        tokens, links = parse_postscript(gutenberg_children_bug, options, sys.stdout)

        self.assertEqual(18, len(tokens))

    @unittest.skip
    def test_parse_gutenchildren_bug_002(self):
        """ Test for number of tokens (bug from Gutenberg Children corpus) """
        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        tokens = parse_tokens(gutenberg_children_bug_002t, options)[0]

        self.assertEqual(tokens, gutenberg_children_bug_002tr)

    @unittest.skip
    def test_parse_postscript_gutenchildren_bug_002(self):

        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        tokens, links = parse_postscript(gutenberg_children_bug_002, options, sys.stdout)

        print(tokens)

        self.assertEqual(12, len(tokens))
        self.assertEqual(6, len(links))

        # pm = parse_metrics(tokens)
        #
        # self.assertEqual(0.0, pm.completely_parsed_ratio)
        # self.assertEqual(0.0, pm.completely_unparsed_ratio)
        # self.assertEqual(0.94117647, float(pm.average_parsed_ratio))

        # self.assertEqual(16.0/17.0, pm.average_parsed_ratio)

    # @unittest.skip
    def test_parse_postscript_alice_bug_001(self):
        """ test_parse_postscript """
        # print(__doc__, sys.stderr)

        options = 0
        # options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(alice_bug_001, options, sys.stdout)

        self.assertEqual(15, len(tokens))

        for link in links:
            self.assertTrue(link[0]<15 and link[1]<15, str(link))

        # self.assertEqual(["most", "people", "start", "at", "our", "web", "site", "which", "has", "the", "main", "pg",
        #                   "search", "facility:"], tokens)

    def test_parse_postscript_alice_bug_002(self):
        """ Gutenberg Children bug test """
        options = 0
        # options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(alice_bug_002, options, sys.stdout)

        self.assertEqual(29, len(tokens), tokens)


    def test_get_link_set(self):
        """ Test for link extraction according to set options """
        # post_all_walls = "[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)]" \
        #                  "[[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)]" \
        #                  "[4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]"
        expected_set = {(1, 2), (2, 5), (2, 3), (4, 5), (5, 6)}
        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_PARSE_QUALITY
        tokens, links = parse_postscript(self.post_all_walls, options, sys.stdout)
        result_set = get_link_set(tokens, links, options)

        self.assertTrue(result_set == expected_set)

    def test_prepare_tokens_both_walls_period_no_options(self):
        """ Test for filtering token list according to set options """
        token_list = ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.', '###RIGHT-WALL###']
        token_list_no_walls = ['dad', 'was', 'not', 'a', 'parent', 'before', '.']
        token_list_no_period = ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '###RIGHT-WALL###']
        token_list_words_only = ['dad', 'was', 'not', 'a', 'parent', 'before']

        # Should take no action
        options = 0 | BIT_RWALL
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list, result_list, "Lists are not the same!!!")

        # Should return a list with no walls only word-tokens and period
        options = 0 | BIT_NO_LWALL
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list_no_walls, result_list, "Lists are not the same!!!")

        # Should return a list with walls, word-tokens and period
        options = 0 | BIT_RWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list_no_period, result_list, "Lists are not the same!!!")

        # Should return a list with no walls and no period
        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list_words_only, result_list, "Lists are not the same!!!")

        tokens_period_in_brackets = ["dad", "[has]", "[a]", "[telescope]", "[.]"]
        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(tokens_period_in_brackets, options)
        self.assertEqual(["dad", "[has]", "[a]", "[telescope]"], result_list, "Lists are not the same!!!")

        tokens_only_period_unboxed = ["[dad]", "has", "[binoculars]", "."]
        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(tokens_only_period_unboxed, options)
        self.assertEqual(["[dad]", "has", "[binoculars]"], result_list, "Lists are not the same!!!")

        seven_dots = ['###LEFT-WALL###', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]', '###RIGHT-WALL###']
        options = 0
        result_list = prepare_tokens(seven_dots, options)
        self.assertEqual(['###LEFT-WALL###', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]'], result_list, "Lists are not the same!!!")

        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(seven_dots, options)
        self.assertEqual(['[.]', '[.]', '[.]', '[.]', '[.]', '[.]'], result_list, "Lists are not the same!!!")

    def test_skip_command_response(self):
        with open("tests/test-data/raw/debug-msg.txt") as file:
            text = file.read()

        pos = skip_command_response(text)

        # print(text[pos:], sys.stderr)
        self.assertEqual(175, pos)

    def test_skip_linkage_header(self):
        pos, err = skip_linkage_header(timeout_linkage)
        print(timeout_linkage[pos:])
        self.assertEqual(219, pos)
        self.assertEqual(PS_PANIC_DETECTED|PS_TIMEOUT_EXPIRED, err)


if __name__ == '__main__':
    unittest.main()
