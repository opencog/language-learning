import unittest

from src.grammar_tester.lgapiparser import *
from src.common.optconst import *
from src.grammar_tester.lginprocparser import LGInprocParser


class LGAPITestCase(unittest.TestCase):

    # @unittest.skip
    def test_parse_file_with_api(self):
        # Testing over poc-turtle corpus... 100% success is expected.

        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_RM_DIR | BIT_LOC_LANG | BIT_PARSE_QUALITY \
                  | BIT_EXISTING_DICT

        lgp = LGInprocParser()
        api = LGApiParser()

        dict = "en"
        corp = "tests/test-data/corpora/poc-english/poc_english.txt"
        # reff = "tests/test-data/corpora/poc-english/poc_english_parses_lg.txt"
        outp = "/var/tmp/temp"
        reff = None

        # dict = "test-data/dict/poc-turtle"
        # corp = "test-data/corpora/poc-turtle/poc-turtle.txt"
        # outp = "test-data/temp"
        # reff = None

        m1, q1 = lgp.parse(dict, corp, outp, reff, options)
        m2, q2 = api.parse(dict, corp, outp, reff, options)

        print(f"q1=\n{q1.parse_quality_str(q1)}\n")
        print(f"q2=\n{q2.parse_quality_str(q2)}\n")

        self.assertTrue(m1 == m2)
        # self.assertTrue(q1 == q2)


if __name__ == '__main__':
    unittest.main()
