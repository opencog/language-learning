import logging
import unittest
import sys
import os

from src.common.optconst import *
from src.link_grammar.lginprocparser2 import LGInprocParser2, LGInprocParserX
from src.common.textprogress import TextProgress
from src.grammar_tester.parsevaluate import load_parses
from src.grammar_tester.lgmisc import LGParseError
from src.common.cliutils import setup_logging
from src.observer.lgobserver import LGPSTokenizer
from src.observer.wordpairs import *

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

lg_post_explosion = \
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

class LGInprocParser2TestCase(unittest.TestCase):
    def setUp(self):
        self.tmp_path = "/var/tmp/parse"

        if not os.path.isdir(self.tmp_path):
            os.mkdir(self.tmp_path)

        setup_logging(logging.DEBUG, logging.DEBUG, f"{self.tmp_path}/LGInprocParser2TestCase.log", "w")

    # @unittest.skip
    # def test_parse_batch_ps_output(self):
    #     """ Test postscript parsing for total number of parsed sentences """
    #     pr = LGInprocParser2()
    #     num_sent = len(pr._parse_batch_ps_output(lg_post_output, 0))
    #     self.assertEqual(num_sent, 12, "'parse_batch_ps_output()' returns '{}' instead of '{}'".format(num_sent, 12))
    #
    # @unittest.skip
    # def test_parse_batch_ps_output_explosion(self):
    #     """ Test for 'combinatorial explosion' """
    #     pr = LGInprocParser2(verbosity=0)
    #     num_sent = len(pr._parse_batch_ps_output(lg_post_explosion, 0))
    #     self.assertEqual(num_sent, 4, "'parse_batch_ps_output()' returns '{}' instead of '{}'".format(num_sent, 4))

    # @unittest.skip
    def test_parse_sent_count(self):

        pr = LGInprocParser2()

        bar = TextProgress(total=12, desc="Overal progress")
        options = BIT_STRIP | BIT_PARSE_QUALITY | BIT_EXISTING_DICT | BIT_LG_EXE | BIT_NO_LWALL #| BIT_OUTPUT_DIAGRAM

        pm, pq = pr.parse("tests/test-data/dict/poc-turtle", "tests/test-data/corpora/poc-turtle/poc-turtle.txt",
                 f"{self.tmp_path}/poc-turtle-20.txt.ull", "tests/test-data/parses/poc-turtle-mst/poc-turtle-parses-expected.txt", options, bar)

        print(pm.text(pm), pq.text(pq))
        self.assertEqual(12, pm.sentences)
        self.assertEqual(12, pq.sentences)

    @unittest.skip
    def test_observer(self):
        corpus = "tests/test-data/corpora/poc-turtle/poc-turtle.txt"
        options = BIT_STRIP | BIT_EXISTING_DICT | BIT_LG_EXE  # | BIT_NO_LWALL
        # options = BIT_EXISTING_DICT | BIT_LG_EXE | BIT_NO_LWALL

        with open("/var/tmp/poc-turtle.txt.fmi", "w") as out_stream:
            pairs = WordPairs()
            proto = LGPSTokenizer(pairs, 24)
            parser = LGInprocParserX(num_linkages=24)
            parser.parse("any", corpus, options, proto)

            # pairs.count_probabilities()
            pairs.count_mi()
            pairs.dump(out_stream)

    # @unittest.skip
    def test_load_ull_file_not_found(self):

        with self.assertRaises(FileNotFoundError) as ctx:
            data = load_parses("/var/tmp/something.txt")

        # self.assertEqual("list index out of range", str(ctx.exception))

    # @unittest.skip
    def test_load_ull_file_access_denied(self):

        with self.assertRaises(PermissionError) as ctx:
            data = load_parses("/root/something.txt")

        # self.assertEqual("list index out of range", str(ctx.exception))

    @unittest.skip
    def test_parse_file_not_found(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            # TestClass().test_func()
            pr = LGInprocParser2()
            pr.parse("tests/test-data/dict/poc-turtle", "tests/test-data/corpora/poc-turtle/poc-turtle.txt",
                     "/var/tmp/parse", "tests/test-data/corpora/poc-turtle/poc-horse.txt", BIT_STRIP | BIT_PARSE_QUALITY)

        # self.assertEqual("list index out of range", str(ctx.exception))

    # @unittest.skip
    def test_parse_invalid_file_format(self):

        with self.assertRaises(LGParseError) as ctx:
            pr = LGInprocParser2()
            pr.parse("tests/test-data/dict/poc-turtle", "tests/test-data/corpora/poc-turtle/poc-turtle.txt",
                     f"{self.tmp_path}/poc-turtle-21.txt.ull", "tests/test-data/corpora/poc-turtle/poc-turtle.txt", BIT_STRIP | BIT_PARSE_QUALITY)

        # self.assertEqual("list index out of range", str(ctx.exception))

    @unittest.skip
    def test_parse_invalid_ref_file(self):

        # with self.assertRaises(LGParseError) as ctx:
        try:
            pr = LGInprocParser2()
            pr.parse("tests/test-data/dict/poc-turtle", "tests/test-data/corpora/poc-english/poc_english.txt",
                     "/var/tmp/parse", "tests/test-data/parses/poc-turtle-mst/poc-turtle-parses-expected.txt",
                     BIT_STRIP | BIT_PARSE_QUALITY)
        except Exception as err:
            print(str(type(err)) + ": " + str(err), file=sys.stderr)


if __name__ == '__main__':
    unittest.main()
