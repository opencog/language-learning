import unittest
import os
import filecmp
from src.common.tokencount import *
from src.common.optconst import *


class TokenCountTestCase(unittest.TestCase):

    output_dir = "/var/tmp/parse"

    def setUp(self) -> None:
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    def test_get_token_counts(self):
        token_counts, total_counts = {}, 0

        options = BIT_EXISTING_DICT | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        total_counts = update_token_counts("tests/test-data/corpora/poc-turtle/poc-turtle.txt", token_counts, options)

        self.assertEqual(36, total_counts)
        self.assertEqual(2, token_counts.get("tuna", 0))
        self.assertEqual(2, token_counts.get("herring", 0))

    def test_dump_tokens(self):
        options = BIT_EXISTING_DICT | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        corpus = "tests/test-data/corpora/poc-turtle/poc-turtle.txt"

        dump_token_counts(corpus, self.output_dir, options)

        self.assertTrue(os.path.exists(self.output_dir + "/poc-turtle.txt.cnt"))

    @unittest.skip
    def test_count_tokens_multi(self):
        options = BIT_EXISTING_DICT | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        corpus_1 = "tests/test-data/corpora/poc-english/poc_english.txt"
        corpus_2 = "tests/test-data/corpora/poc-english-multi"

        dump_token_counts(corpus_1, self.output_dir, options)
        dump_token_counts(corpus_2, self.output_dir, options)

        output_1 = self.output_dir + "/poc_english.txt.cnt"
        output_2 = self.output_dir + "/poc-english-multi.cnt"

        self.assertTrue(os.path.exists(output_1))
        self.assertTrue(os.path.exists(output_2))
        self.assertTrue(filecmp.cmp(output_1, output_2, False))

    def test_load_token_counts(self):
        options = BIT_EXISTING_DICT | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        corpus_1 = "tests/test-data/corpora/poc-english/poc_english.txt"

        dump_token_counts(corpus_1, self.output_dir, options)

        token_counts_1 = count_tokens(corpus_1, options)

        output_1 = self.output_dir + "/poc_english.txt.cnt"

        token_counts_2 = load_token_counts(output_1)

        self.assertEqual(token_counts_1, token_counts_2)


if __name__ == '__main__':
    unittest.main()
