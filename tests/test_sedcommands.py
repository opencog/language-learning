import unittest
from subprocess import PIPE, Popen

from src.common.sedcommands import get_sed_cmd_common_part
from src.common.optconst import *


class RegexTestCase(unittest.TestCase):

    def sed_exec(self, sed_cmd: list) -> str:

        with Popen(sed_cmd, stdout=PIPE) as sed_proc:
            text_stream = sed_proc.communicate()[0]

        return text_stream.decode("utf-8-sig").strip()

    def test_sentences_in_old_ull(self):

        corpus = "tests/test-data/regex-test/regex-test.txt.ull"

        text = self.sed_exec(get_sed_cmd_common_part(BIT_ULL_IN) + [corpus])

        with open("tests/test-data/regex-test/regex-test-result.txt", "r") as ref:
            ref_text = ref.read().strip()

        self.assertEqual(ref_text, text)
        self.assertEqual(30, len(text.split("\n")))

    def test_sentences_in_old_ull_lcase(self):

        corpus = "tests/test-data/regex-test/regex-test.txt.ull"

        text = self.sed_exec(get_sed_cmd_common_part(BIT_ULL_IN | BIT_INPUT_TO_LCASE) + [corpus])

        with open("tests/test-data/regex-test/regex-test-result-lcase.txt", "r") as ref:
            ref_text = ref.read().strip()

        self.assertEqual(ref_text, text)
        self.assertEqual(30, len(text.split("\n")))

    def test_sentences_in_new_ull(self):

        corpus = "tests/test-data/regex-test/ull-new.txt.ull"

        text = self.sed_exec(get_sed_cmd_common_part(BIT_ULL_IN) + [corpus])

        self.assertEqual(20, len(text.split("\n")))


if __name__ == '__main__':
    unittest.main()
