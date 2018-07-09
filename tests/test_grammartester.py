import unittest
from decimal import Decimal
from grammar_tester.grammartester import GrammarTester, test_grammar, test_grammar_cfg
from grammar_tester.lginprocparser import LGInprocParser
from grammar_tester.lgapiparser import LGApiParser
from grammar_tester.optconst import *
# from common.cliutils import handle_path_string

from common.fileconfman import JsonFileConfigManager
from common.cliutils import handle_path_string
from grammar_tester.textfiledashb import TextFileDashboard

tmpl = "/home/alex/data/dict/poc-turtle"
grmr = "/home/alex/data/dict"
limit = 100
# opts = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR #| BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY #| BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT
opts = BIT_SEP_STAT | BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_DPATH_CREATE | BIT_LOC_LANG | BIT_PARSE_QUALITY #| BIT_ULL_IN #| BIT_OUTPUT_DIAGRAM #| BIT_SEP_STAT

# # PubMed-2018-06-01 parse for ULL reference
# dict = "en"
# corp = "/home/alex/data2/parses/PubMed-2018-06-01/data"
# dest = "/home/alex/data2/parses/PubMed-2018-06-01/ref"
# ref = None


# PubMed-2018-06-01 parse with learned grammar
dict = "/home/alex/data2/parses/PubMed-2018-06-01-splitted/dict"
corp = "/home/alex/data2/parses/PubMed-2018-06-01-splitted/data"
dest = "/home/alex/data2/parses/PubMed-2018-06-01-splitted/parses"
ref = "/home/alex/data2/parses/PubMed-2018-06-01-splitted/ref"


class ParseTestCase(unittest.TestCase):

    # @unittest.skip
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


@unittest.skip
class GrammarTesterTestCase(unittest.TestCase):

    @unittest.skip
    def test_test_with_conf(self):
        # conf_path = "test-data/config/AGI-2018.json"
        conf_path = "test-data/config/AGI-2018-no-dashboard.json"

        pm, pq = test_grammar_cfg(conf_path)

        # self.assertEqual(25, gt._total_dicts)
        self.assertEqual(88, pm.sentences)

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
        dict = "poc-turtle"
        # dict = handle_path_string("test-data/dict/poc-turtle")
        corp = handle_path_string("test-data/corpora/poc-english/poc_english.txt")
        dest = handle_path_string("test-data/temp")
        ref = None  # "/home/alex/data/poc-english/poc_english_noamb_parse_ideal.txt"

        pr = LGInprocParser()
        # pr = LGApiParser()

        # print(dict, corp, dest, ref, sep="\n")

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm, pq = gt.test(dict, corp, dest, ref, opts)

        print(pm.text(pm))
        # print(pq.text(pq))

        # self.assertEqual(25, gt._total_dicts)
        self.assertEqual(88, pm.sentences)
        self.assertEqual("2.46%", pm.parseability_str(pm).strip())
        self.assertEqual("90.91%", pm.completely_unparsed_str(pm).strip())

    # @unittest.skip
    def test_parseability_multi_file(self):
        """ Test poc-english corpus with poc-turtle dictionary """
        dict = "poc-turtle"
        # dict = handle_path_string("test-data/dict/poc-turtle")
        corp = handle_path_string("test-data/corpora/poc-english-multi")
        dest = handle_path_string("test-data/temp")
        ref = None  # handle_path_string("test-data/parses/poc-english-multi-ref")

        pr = LGInprocParser()
        # pr = LGApiParser()

        # print(dict, corp, dest, ref, sep="\n")

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm, pq = gt.test(dict, corp, dest, ref, opts)

        print(pm.text(pm))
        # print(pq.text(pq))

        self.assertEqual(9, gt._total_files)
        self.assertEqual(88, pm.sentences)
        self.assertEqual("2.46%", pm.parseability_str(pm).strip())
        self.assertEqual("90.91%", pm.completely_unparsed_str(pm).strip())


    # @unittest.skip
    def test_parseability_coinsedence(self):
        """ Test poc-english corpus with poc-turtle dictionary """
        dict = "en"  # "poc-turtle"
        # dict = handle_path_string("test-data/dict/poc-turtle")
        corp1 = handle_path_string("test-data/corpora/poc-english/poc_english.txt")
        corp2 = handle_path_string("test-data/corpora/poc-english-multi")
        dest = handle_path_string("test-data/temp")
        ref1 = handle_path_string("test-data/parses/poc-english-ref/poc_english.txt.ull")
        ref2 = handle_path_string("test-data/parses/poc-english-multi-ref")

        pr = LGInprocParser()
        # pr = LGApiParser()

        gt = GrammarTester(grmr, tmpl, limit, pr)
        pm1, pq1 = gt.test(dict, corp1, dest, ref1, opts)
        pm2, pq2 = gt.test(dict, corp2, dest, ref2, opts)

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
