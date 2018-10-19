import unittest
import os
import sys
from decimal import Decimal
from subprocess import Popen, PIPE

from src.grammar_tester.grammartester import GrammarTester, test_grammar, test_grammar_cfg
from src.grammar_tester.lginprocparser import LGInprocParser
from src.grammar_tester.lgapiparser import LGApiParser
from src.grammar_tester.optconst import *

from src.common.fileconfman import JsonFileConfigManager
from src.common.cliutils import handle_path_string
from src.grammar_tester.textfiledashb import TextFileDashboard

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

# class ParseTestCase(unittest.TestCase):
#
#     @unittest.skip
#     def test_test(self):
#         pr = LGInprocParser()
#         # pr = LGApiParser()
#
#         print(dict, corp, dest, ref, sep="\n")
#
#         gt = GrammarTester(grmr, tmpl, limit, pr)
#         pm, pq = gt.test(dict, corp, dest, ref, opts)
#
#         print(pm.text(pm))
#         # print(pq.text(pq))
#
#         # self.assertEqual(25, gt._total_dicts)
#         self.assertEqual(88, pm.sentences)


# @unittest.skip
class GrammarTesterTestCase(unittest.TestCase):

    @unittest.skip
    def test_test_with_conf(self):
        # conf_path = "test-data/config/AGI-2018.json"
        conf_path = "tests/test-data/config/AGI-2018-no-dashboard.json"

        pm, pq, pqa = test_grammar_cfg(conf_path)

        # self.assertEqual(25, gt._total_dicts)
        self.assertEqual(88, pm.sentences)

    @unittest.skip
    def test_test_grammar(self):
        input_grammar = "tests/test-data/parses/AGI-2018-paper-data-2018-04-22/POC-English-NoAmb-LEFT-WALL+period"
        input_corpus = "tests/test-data/corpora/poc-english/poc_english_noamb.txt"
        template_path = "tests/test-data/dict/poc-turtle"
        grammar_root = "/var/tmp/"
        output_path = "tests/test-data/parses/AGI-2018-paper-data-2018-04-22/POC-English-NoAmb-LEFT-WALL+period"
        ref_path = "tests/test-data/parses/poc-english-ref/poc_english_noamb.txt.ull"

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        pa, f1, pr, rc = test_grammar(input_corpus, output_path, input_grammar, grammar_root, template_path, 1000,
                                   options, ref_path)

        print("PA: {:2.4f}\nF1: {:2.4f}\nPrecision: {:2.4f}\nRecall: {:2.4f}\n".format(pa, f1, pr, rc))

        # with Popen(["echo", "dummy_line"], stdout=PIPE) as proc_echo , \
        #         Popen(["link-parser", "-verbosity=1"], stdin=proc_echo.stdout, stdout=PIPE, stderr=PIPE) as proc_link, \
        #         Popen(["grep", "Library version"], stdin=proc_link.stderr, stdout=PIPE, stderr=PIPE) as proc_grep:
        # 
        #     proc_echo.stdout.close()
        # 
        #     # Closing grep output stream will terminate it's process.
        #     proc_link.stdout.close()
        # 
        #     # Read pipes to get complete output returned by 'conda'
        #     raw, err = proc_grep.communicate()
        # 
        #     print(raw.decode(), file=sys.stderr)
        #     # print("err:", err.decode(), file=sys.stderr)


        self.assertAlmostEqual(Decimal("0.8167"), pa, 2)
        self.assertAlmostEqual(Decimal("0.5670"), f1, 2)
        self.assertAlmostEqual(Decimal("0.6065"), pr, 2)
        self.assertAlmostEqual(Decimal("0.5324"), rc, 2)

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
        dest = handle_path_string("tests/test-data/temp")
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
        dest = handle_path_string("tests/test-data/temp")
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
        dest = handle_path_string("tests/test-data/temp")
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
