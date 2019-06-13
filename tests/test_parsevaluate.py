import unittest
import sys
from src.grammar_tester.parsevaluate import *
from src.common.optconst import *


parse_no_wall = """tuna isa fish . 
0 tuna 1 isa
1 isa 2 fish
2 fish 3 .
"""

parse_with_wall = """tuna isa fish . 
0 ###LEFT-WALL### 1 tuna
1 tuna 2 isa
2 isa 3 fish
3 fish 4 .
"""

# parse_with_wall = """tuna isa fish .
# 0 ###LEFT-WALL### 1 tuna
# 1 tuna 2 isa
# 2 isa 3 fish
# 3 fish 4 .
# """

class TestEvalMethods(unittest.TestCase):

    # @unittest.skip
    def test_get_parses(self):
        """ Test evaluation """
        ref_parses = load_parses("tests/test-data/parses/poc-turtle-mst/one-parse-expected.txt")
        test_parses = load_parses("tests/test-data/parses/poc-turtle-mst/one-parse-expected-mi.txt")
        eval_parses(test_parses, ref_parses, 0x00000000 | BIT_ULL_IN | BIT_NO_LWALL | BIT_NO_PERIOD)
        self.assertEqual(ref_parses, test_parses)

    # # @unittest.skip
    # def test_get_parses(self):
    #     """ Test evaluation """
    #     ref_data = load_ull_file("tests/test-data/parses/poc-turtle-mst/one-parse-expected.txt")
    #     test_data = load_ull_file("tests/test-data/parses/poc-turtle-mst/one-parse-expected-mi.txt")
    #     # print("ref_data='", ref_data, "'", file=sys.stderr)
    #     # print("test_data='", test_data, "'", file=sys.stderr)
    #     ref_parses = get_parses(ref_data)
    #     test_parses = get_parses(test_data)
    #     eval_parses(test_parses, ref_parses, 0x00000000 | BIT_ULL_IN | BIT_NO_LWALL | BIT_NO_PERIOD)
    #     self.assertEqual(ref_parses, test_parses)

    @unittest.skip
    def test_get_parses_bug(self):
        """ Test for found bug in get_parses() """
        test_data = load_ull_file("tests/test-data/corpora/poc-english/poc_english_noamb_parses_1s_2.txt")
        test_parses = get_parses(test_data)
        # print(test_parses, file=sys.stderr)
        self.assertEqual(2, len(test_parses[0][1]))

        ref_data = load_ull_file("tests/test-data/corpora/poc-english/poc_english_noamb_parses_ideal_1s_2.txt")
        ref_parses = get_parses(ref_data)
        # print(ref_parses, file=sys.stderr)
        self.assertEqual(4, len(ref_parses[0][1]))

    def test_compare_ull_files_with_lw(self):
        """ Test for proper comparison of parses with LW """
        pq1 = compare_ull_files("tests/test-data/corpora/poc-english/poc_english_noamb_parses_ideal_1s_2.txt",
                                "tests/test-data/corpora/poc-english/poc_english_noamb_parses_ideal_1s_2.txt",
                                0x00000000 | BIT_ULL_IN)

        # print(pq1.text(pq1), file=sys.stderr)

        self.assertEqual(1.0, pq1.quality)
        self.assertEqual(7.0, pq1.total)
        self.assertEqual(0.0, pq1.ignored)
        self.assertEqual(0.0, pq1.missing)
        self.assertEqual(0.0, pq1.extra)

    def test_compare_ull_files_no_lw(self):
        """ Test for proper comparison of parses without LW """
        pq1 = compare_ull_files("tests/test-data/corpora/poc-english/poc_english_noamb_parses_ideal_1s_2.txt",
                                "tests/test-data/corpora/poc-english/poc_english_noamb_parses_ideal_1s_2.txt",
                                0x00000000 | BIT_ULL_IN | BIT_NO_LWALL | BIT_NO_PERIOD)

        # print(pq1.text(pq1), file=sys.stderr)

        self.assertEqual(1.0, pq1.quality)
        self.assertEqual(4.0, pq1.total)
        self.assertEqual(3.0, pq1.ignored)
        self.assertEqual(0.0, pq1.missing)
        self.assertEqual(0.0, pq1.extra)

    # @unittest.skip
    def test_get_parses_start_from_digit(self):
        """ Test evaluation """
        ref_parses = load_parses("tests/test-data/parses/start-from-digit/start-from-digit.ull")
        test_parses = load_parses("tests/test-data/parses/start-from-digit/start-from-digit.ull")
        # eval_parses(test_parses, ref_parses, False, sys.stderr)
        self.assertEqual(ref_parses, test_parses)

    # # @unittest.skip
    # def test_get_parses_start_from_digit(self):
    #     """ Test evaluation """
    #     ref_data = load_ull_file("tests/test-data/parses/start-from-digit/start-from-digit.ull")
    #     test_data = load_ull_file("tests/test-data/parses/start-from-digit/start-from-digit.ull")
    #     # print("ref_data='", ref_data, "'", file=sys.stderr)
    #     # print("test_data='", test_data, "'", file=sys.stderr)
    #     ref_parses = get_parses(ref_data)
    #     test_parses = get_parses(test_data)
    #     # eval_parses(test_parses, ref_parses, False, sys.stderr)
    #     self.assertEqual(ref_parses, test_parses)


if __name__ == '__main__':
    unittest.main()