import unittest
import os
from decimal import Decimal

from src.grammar_tester.grammartester import GrammarTester, test_grammar  # , test_grammar_cfg
from src.grammar_tester.lginprocparser import LGInprocParser
from src.common.optconst import *

from src.common.cliutils import handle_path_string

tmpl = "tests/test-data/dict/poc-turtle"
grmr = "tests/test-data/dict"
limit = 1000
opts = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR #| BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY #| BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
# opts = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY #| BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT

# opts = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY | BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT

# Test poc-english corpus with poc-turtle dictionary
dict = "poc-turtle"
corp = "/home/alex/data/corpora/poc-english/poc_english.txt"
dest = "/home/alex/data2/parses"
ref = None  # "/home/alex/data/poc-english/poc_english_noamb_parse_ideal.txt"


# @unittest.skip
class GrammarTesterTestCase(unittest.TestCase):

    @staticmethod
    def create_path(path: str):
        if path is not None and not os.path.isdir(path):
            os.makedirs(path)

    @unittest.skip
    def test_test_with_conf(self):
        # conf_path = "test-data/config/AGI-2018.json"
        conf_path = "tests/test-data/config/AGI-2018-no-dashboard.json"

        pm, pq, pqa = test_grammar_cfg(conf_path)

        # self.assertEqual(25, gt._total_dicts)
        self.assertEqual(88, pm.sentences)

    @unittest.skip
    def test_test_grammar(self):
        input_grammar = "en"
        # input_grammar = "tests/test-data/parses/AGI-2018-paper-data-2018-04-22/POC-English-NoAmb-LEFT-WALL+period"
        input_corpus = "tests/test-data/corpora/poc-english/poc_english_noamb.txt"
        template_path = "tests/test-data/dict/poc-turtle"

        grammar_root = "/var/tmp/test_grammar"
        self.create_path(grammar_root)
        output_path = "/var/tmp/test_grammar/AGI-2018-paper-data-2018-04-22/POC-English-NoAmb-LEFT-WALL+period"
        self.create_path(output_path)

        ref_path = "tests/test-data/parses/poc-english-ref/poc_english_noamb.txt.ull"

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN | BIT_LG_GR_NAME
        # options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        pa, f1, pr, rc = test_grammar(input_corpus, output_path, input_grammar, grammar_root, template_path, 1000,
                                   options, ref_path)

        print("PA: {:2.4f}\nF1: {:2.4f}\nPrecision: {:2.4f}\nRecall: {:2.4f}\n".format(pa, f1, pr, rc))

        self.assertAlmostEqual(Decimal("1.0"), pa, 2)
        self.assertAlmostEqual(Decimal("1.0"), f1, 2)
        self.assertAlmostEqual(Decimal("1.0"), pr, 2)
        self.assertAlmostEqual(Decimal("1.0"), rc, 2)

        # self.assertAlmostEqual(Decimal("0.8167"), pa, 2)
        # self.assertAlmostEqual(Decimal("0.5670"), f1, 2)
        # self.assertAlmostEqual(Decimal("0.6065"), pr, 2)
        # self.assertAlmostEqual(Decimal("0.5324"), rc, 2)

    # @unittest.skip
    def test_test_grammar_1(self):
        input_grammar = "tests/test-data/metrics-test/1"
        input_corpus = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"
        template_path = "tests/test-data/dict/poc-turtle"

        grammar_root = "/var/tmp/test_grammar_1/"
        output_path = "/var/tmp/test_grammar_1"
        self.create_path(grammar_root)
        self.create_path(output_path)

        ref_path = input_corpus

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        pa, f1, pr, rc = test_grammar(input_corpus, output_path, input_grammar, grammar_root, template_path, 1000,
                                   options, ref_path)

        print("PA: {:2.4f}\nF1: {:2.4f}\nPrecision: {:2.4f}\nRecall: {:2.4f}\n".format(pa, f1, pr, rc))

        self.assertAlmostEqual(Decimal("1.0"), pa, 2)
        self.assertAlmostEqual(Decimal("1.0"), f1, 2)
        self.assertAlmostEqual(Decimal("1.0"), pr, 2)
        self.assertAlmostEqual(Decimal("1.0"), rc, 2)

    # @unittest.skip
    def test_test_grammar_2(self):
        input_grammar = "tests/test-data/metrics-test/2"
        input_corpus = "tests/test-data/metrics-test/poc-turtle-parses-win6.txt"
        template_path = "tests/test-data/dict/poc-turtle"
        grammar_root = "/var/tmp/test_grammar_2/"
        output_path = "/var/tmp/test_grammar_2/"
        self.create_path(grammar_root)

        ref_path = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        pa, f1, pr, rc = test_grammar(input_corpus, output_path, input_grammar, grammar_root, template_path, 1000,
                                   options, ref_path)

        print("PA: {:2.4f}\nF1: {:2.4f}\nPrecision: {:2.4f}\nRecall: {:2.4f}\n".format(pa, f1, pr, rc))

        self.assertAlmostEqual(Decimal("1.0"), pa, 2)
        self.assertAlmostEqual(Decimal("0.5"), f1, 2)
        self.assertAlmostEqual(Decimal("0.5"), pr, 2)
        self.assertAlmostEqual(Decimal("0.5"), rc, 2)

    @unittest.skip
    def test_test(self):
        pr = LGInprocParser()
        # pr = LGApiParser()

        print(dict, corp, dest, ref, sep="\n")

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm, pq = gt.test(dict, corp, dest, ref, opts)

        print(pm.text(pm))
        # print(pq.text(pq))

        # self.assertEqual(25, gt._total_dicts)
        self.assertEqual(88, pm.sentences)


    # @unittest.skip
    def test_parseability(self):
        """ Test poc-english corpus with poc-turtle dictionary """
        # dict = "poc-turtle"
        dict = handle_path_string("tests/test-data/dict/poc-turtle")
        corp = handle_path_string("tests/test-data/corpora/poc-english/poc_english.txt")
        dest = handle_path_string("/var/tmp/test_parseability")
        self.create_path(dest)

        # dest = handle_path_string("tests/test-data/temp")
        ref = None  # "/home/alex/data/poc-english/poc_english_noamb_parse_ideal.txt"

        pr = LGInprocParser()
        # pr = LGApiParser()

        # print(dict, corp, dest, ref, sep="\n")

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm, pq = gt.test(dict, corp, dest, ref, (opts | BIT_EXISTING_DICT))

        # print(pm.text(pm))
        # print(pq.text(pq))

        # self.assertEqual(25, gt._total_dicts)
        self.assertEqual(88, pm.sentences)
        self.assertEqual("2.46%", pm.parseability_str(pm).strip())
        self.assertEqual("90.91%", pm.completely_unparsed_str(pm).strip())

    # @unittest.skip
    def test_parseability_multi_file(self):
        """ Test poc-english corpus with poc-turtle dictionary """
        # dict = "poc-turtle"
        dict = handle_path_string("tests/test-data/dict/poc-turtle")
        corp = handle_path_string("tests/test-data/corpora/poc-english-multi")
        dest = handle_path_string("/var/tmp/test_parseability_multi_file")
        self.create_path(dest)

        # dest = handle_path_string("tests/test-data/temp")
        ref = None  # handle_path_string("test-data/parses/poc-english-multi-ref")

        pr = LGInprocParser()
        # pr = LGApiParser()

        # print(dict, corp, dest, ref, sep="\n")

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm, pq = gt.test(dict, corp, dest, ref, (opts | BIT_EXISTING_DICT))

        # print(pm.text(pm))
        # print(pq.text(pq))

        # self.assertEqual(9, gt._total_files)
        self.assertEqual(88, pm.sentences)
        self.assertEqual("2.46%", pm.parseability_str(pm).strip())
        self.assertEqual("90.91%", pm.completely_unparsed_str(pm).strip())


    # @unittest.skip
    def test_parseability_coinsedence(self):
        """ Test for coinsidence of results of parsing poc-english corpus in a single file and the one splited into multiple files """
        dict = "en"
        # dict = handle_path_string("tests/test-data/dict/poc-turtle")
        corp1 = handle_path_string("tests/test-data/corpora/poc-english/poc_english.txt")
        corp2 = handle_path_string("tests/test-data/corpora/poc-english-multi")
        dest = handle_path_string("/var/tmp/test_parseability_coinsedence")
        self.create_path(dest)

        # dest = handle_path_string("tests/test-data/temp")
        ref1 = handle_path_string("tests/test-data/parses/poc-english-ref/poc_english.txt.ull")
        ref2 = handle_path_string("tests/test-data/parses/poc-english-multi-ref")

        pr = LGInprocParser()
        # pr = LGApiParser()

        # opts |= BIT_EXISTING_DICT

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm1, pq1 = gt.test(dict, corp1, dest, ref1, (opts | BIT_EXISTING_DICT))
        pm2, pq2 = gt.test(dict, corp2, dest, ref2, (opts | BIT_EXISTING_DICT))

        # print(pm.text(pm))
        # print(pq.text(pq))

        self.assertEqual(pm1, pm2)
        self.assertEqual(pq1, pq2)

        # self.assertEqual(88, pm.sentences)
        self.assertEqual("100.00%", pm1.parseability_str(pm1).strip())
        self.assertEqual("0.00%", pm1.completely_unparsed_str(pm1).strip())
        self.assertEqual("100.00%", pm1.completely_parsed_str(pm1).strip())


if __name__ == '__main__':
    unittest.main()
