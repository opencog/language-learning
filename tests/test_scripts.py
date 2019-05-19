import os
import sys
import shutil

import unittest
from .script_integration import ScriptIntegrationTestCase

"""
CLI SCRIPT INTEGRATION TESTS

In order to create additional test one should complete the following steps:

"""

# Root path for all pipeline integration tests
TESTS_ROOT = "tests/test-data/cli-scripts"


class CLIScriptsTestCase(ScriptIntegrationTestCase):

    # @unittest.skip
    def test_parse_evaluator_std_mode(self):
        """ 'parse-evaluator' standard evaluation mode integration test performed on POC-English corpus """
        corpus_path = "tests/test-data/parses/poc-english-ref/poc_english.txt.ull"

        test_dir = self.prepare_test_dir(f"{TESTS_ROOT}/parse-evaluator/std-mode", corpus_path)
        out_file = f"{test_dir}/output.txt"
        out_stat = f"{test_dir}/poc_english.txt.ull.stat"

        self.run_script(f"parse-evaluator -t {corpus_path} -r {corpus_path} -O {test_dir} --verbosity=debug", out_file)

        self.assertTrue(os.path.isfile(out_file), f"'{out_file}' does not exist.")
        self.assertTrue(os.path.isfile(out_stat), f"'{out_stat}' does not exist.")
        self.assertTrue(self.compare_text_files(out_stat, f"{out_stat}.expected"))

    def test_parse_evaluator_ord_multi(self):
        """ 'parse-evaluator' evaluation mode integration test performed on multi-file POC-English corpus """
        corpus_path = "tests/test-data/parses/poc-english-multi-ref"

        test_dir = self.prepare_test_dir(f"{TESTS_ROOT}/parse-evaluator/ord-eval-multi", corpus_path)
        out_file = f"{test_dir}/output.txt"
        out_stat = f"{test_dir}/poc-english-multi-ref.stat"

        self.run_script(f"parse-evaluator -t {corpus_path} -r {corpus_path} -O {test_dir} --verbosity=debug", out_file)

        self.assertTrue(os.path.isfile(out_file), f"'{out_file}' does not exist.")
        self.assertTrue(os.path.isfile(out_stat), f"'{out_stat}' does not exist.")
        self.assertTrue(self.compare_text_files(out_stat, f"{out_stat}.expected"))


    # @unittest.skip
    def test_parse_evaluator_seq_mode(self):
        """ 'parse-evaluator' sequential mode integration test performed on POC-English corpus """
        corpus_path = "tests/test-data/parses/poc-english-ref/poc_english.txt.ull"

        test_dir = self.prepare_test_dir(f"{TESTS_ROOT}/parse-evaluator/seq-mode", corpus_path)
        out_file = f"{test_dir}/ord-output.txt"
        out_stat = f"{test_dir}/poc_english.txt.ull.stat"
        out_ull = f"{test_dir}/poc_english.txt.ull.ull"

        # Run script in ordinary mode
        self.run_script(f"parse-evaluator -t {corpus_path} -r {corpus_path} -O {test_dir} -s -i", out_file)

        self.assertTrue(os.path.isfile(out_file), f"'{out_file}' does not exist.")
        self.assertTrue(os.path.isfile(out_stat), f"'{out_stat}' does not exist.")
        self.assertTrue(os.path.isfile(out_stat), f"'{out_ull}' does not exist.")
        self.assertTrue(self.compare_text_files(out_ull, f"{out_ull}.expected"))
        self.assertTrue(self.compare_text_files(out_stat, f"{out_stat}.expected"))

        out_file = f"{test_dir}/alt-output.txt"
        out_seq = f"{test_dir}/sequential_parses.ull"

        # Run script in alternative mode
        self.run_script(f"parse-evaluator -t {corpus_path} -r {corpus_path} -O {test_dir} -s -i -a", out_file)

        self.assertTrue(os.path.isfile(out_file), f"'{out_file}' does not exist.")
        self.assertTrue(self.compare_text_files(out_file, f"{out_file}.expected"))

        self.assertTrue(os.path.isfile(out_seq), f"'{out_seq}' does not exist.")
        self.assertTrue(self.compare_text_files(out_seq, f"{out_seq}.expected"))

    # @unittest.skip
    def test_parse_evaluator_ord_rnd_single(self):
        """ 'parse-evaluator' random mode integration test performed on POC-English corpus """
        corpus_path = "tests/test-data/parses/poc-english-ref/poc_english.txt.ull"

        test_dir = self.prepare_test_dir(f"{TESTS_ROOT}/parse-evaluator/ord-rnd-single", corpus_path)
        out_file = f"{test_dir}/ord-output.txt"
        out_stat = f"{test_dir}/poc_english.txt.ull.stat"
        out_ull = f"{test_dir}/poc_english.txt.ull.ull"

        # Run script in ordinary mode
        self.run_script(f"parse-evaluator -t {corpus_path} -r {corpus_path} -O {test_dir} -z -i", out_file)

        self.assertTrue(os.path.isfile(out_file), f"'{out_file}' does not exist.")
        self.assertTrue(os.path.isfile(out_stat), f"'{out_stat}' does not exist.")
        self.assertTrue(os.path.isfile(out_stat), f"'{out_ull}' does not exist.")
        self.assertTrue(self.compare_text_files(out_ull, f"{out_ull}.expected"))
        self.assertTrue(self.compare_text_files(out_stat, f"{out_stat}.expected"))


if __name__ == '__main__':
    unittest.main()
