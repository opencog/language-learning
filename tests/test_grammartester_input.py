import unittest
import os
from src.grammar_tester.grammartester import GrammarTester
from src.grammar_tester.lginprocparser import LGInprocParser
from src.common.optconst import *


class GTInputTestCase(unittest.TestCase):

    @staticmethod
    def create_path(path: str):
        if path is not None and not os.path.isdir(path):
            os.makedirs(path)

    def setUp(self):
        self.parser = LGInprocParser()

    # @unittest.skip
    def test_input_nonexisting_language(self):
        """ Non existing language parameter test """
        temp_subdir = "nonexisting_dict_dir"
        dict_path = "/home/2035468709-238"
        corpus_path = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"
        template_path = "tests/test-data/dict/poc-turtle"

        grammar_root = "/var/tmp/" + temp_subdir
        output_path = "/var/tmp/" + temp_subdir
        self.create_path(grammar_root)
        self.create_path(output_path)

        ref_path = corpus_path

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        gt = GrammarTester(grammar_root, template_path, 100, self.parser)

        with self.assertRaises(FileNotFoundError) as ctx:
            pm, pq = gt.test(dict_path, corpus_path, output_path, ref_path, options)

        # self.assertEqual("Path '" + dict_path + "' does not exist.", str(ctx.exception))

    # @unittest.skip
    def test_input_nonexisting_corpus(self):
        """ Non existing language parameter test """
        temp_subdir = "nonexisting_corpus_dir"
        dict_path = "tests/test-data/dict/poc-turtle"
        corpus_path = "tests/test-data/metrics-test/poc-dog"
        template_path = "tests/test-data/dict/poc-turtle"

        grammar_root = "/var/tmp/" + temp_subdir
        output_path = "/var/tmp/" + temp_subdir
        self.create_path(grammar_root)
        self.create_path(output_path)

        ref_path = corpus_path

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        gt = GrammarTester(grammar_root, template_path, 100, self.parser)

        with self.assertRaises(FileNotFoundError) as ctx:
            pm, pq = gt.test(dict_path, corpus_path, output_path, ref_path, options)

        # self.assertEqual("Path '" + dict_path + "' does not exist.", str(ctx.exception))

    # @unittest.skip
    def test_input_nonexisting_template(self):
        """ Non existing language parameter test """
        temp_subdir = "nonexisting_template_dir"
        dict_path = "tests/test-data/dict/poc-turtle"
        corpus_path = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"
        template_path = "tests/test-data/dict/poc-dog"

        grammar_root = "/var/tmp/" + temp_subdir
        output_path = "/var/tmp/" + temp_subdir
        self.create_path(grammar_root)
        self.create_path(output_path)

        ref_path = corpus_path

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        gt = GrammarTester(grammar_root, template_path, 100, self.parser)

        with self.assertRaises(FileNotFoundError) as ctx:
            pm, pq = gt.test(dict_path, corpus_path, output_path, ref_path, options)

        # self.assertEqual("Path '" + dict_path + "' does not exist.", str(ctx.exception))

    # @unittest.skip
    def test_input_improper_template(self):
        """ Improper template dir test """
        temp_subdir = "improper_template_dir"
        dict_path = "tests/test-data/dict-files/poc-turtle_2C_2018-03-14_0007.4.0.dict"
        corpus_path = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"
        template_path = "tests/test-data/metrics-test"

        grammar_root = "/var/tmp/" + temp_subdir
        output_path = "/var/tmp/" + temp_subdir
        self.create_path(grammar_root)
        self.create_path(output_path)

        ref_path = corpus_path

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        gt = GrammarTester(grammar_root, template_path, 100, self.parser)

        with self.assertRaises(FileNotFoundError) as ctx:
            pm, pq = gt.test(dict_path, corpus_path, output_path, ref_path, options)

        # self.assertEqual("Path '" + dict_path + "' does not exist.", str(ctx.exception))

    # @unittest.skip
    def test_input_nonexisting_grammar_root(self):
        """ Non existing grammar root dir test """
        temp_subdir = "nonexisting_grammar_dir"
        dict_path = "tests/test-data/dict-files/poc-turtle_2C_2018-03-14_0007.4.0.dict"
        corpus_path = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"
        template_path = "tests/test-data/dict/poc-turtle"

        grammar_root = "/var/tmp/wefgb345ui"
        output_path = "/var/tmp/" + temp_subdir
        # self.create_path(grammar_root)
        self.create_path(output_path)

        ref_path = corpus_path

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        gt = GrammarTester(grammar_root, template_path, 100, self.parser)

        with self.assertRaises(FileNotFoundError) as ctx:
            pm, pq = gt.test(dict_path, corpus_path, output_path, ref_path, options)

        # self.assertEqual("Path '" + dict_path + "' does not exist.", str(ctx.exception))

    # @unittest.skip
    def test_input_nonexisting_output(self):
        """ Non existing output dir test """
        temp_subdir = "nonexisting_grammar_dir"
        dict_path = "tests/test-data/dict-files/poc-turtle_2C_2018-03-14_0007.4.0.dict"
        corpus_path = "tests/test-data/metrics-test/poc-turtle-parses-gold.txt"
        template_path = "tests/test-data/dict/poc-turtle"

        grammar_root = "/var/tmp/" + temp_subdir
        output_path = "/var/tmp/6745uretwrt"
        self.create_path(grammar_root)
        # self.create_path(output_path)

        ref_path = corpus_path

        options = BIT_LG_EXE | BIT_NO_LWALL | BIT_NO_PERIOD | BIT_PARSE_QUALITY | BIT_RM_DIR | BIT_ULL_IN

        gt = GrammarTester(grammar_root, template_path, 100, self.parser)

        with self.assertRaises(FileNotFoundError) as ctx:
            pm, pq = gt.test(dict_path, corpus_path, output_path, ref_path, options)

        # self.assertEqual("Path '" + dict_path + "' does not exist.", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
