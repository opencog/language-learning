import os
import sys
import shutil
import unittest
from subprocess import PIPE, Popen

# Root path where all LG dictionary subdirectories are located
DICT_REL_PATH = "tests/test-data/dict"

# Root path for all pipeline integration tests
TESTS_ROOT = "tests/test-data/pipeline"


class PipelineIntegrationTestCase(unittest.TestCase):
    """
    Pipeline integration test base class

    """
    @staticmethod
    def run_pipeline(config_path: str) -> int:
        """
        Run pipeline defined by JSON configuration file

        :param config_path:     JSON configuration file.
        :return:                OS error level
        """
        ull_cli = shutil.which("ull-cli")

        if ull_cli is None:
            raise FileNotFoundError("'ull-cli' is not found.")

        with Popen([ull_cli, "-C", config_path, "--logging=debug"], stdout=PIPE) as proc:
            proc.communicate()

            ret_code = proc.returncode

        return ret_code

    @staticmethod
    def _cmp_summaries(test_path: str, ref_path: str) -> bool:
        """
        Compare pipeline dash board summaries

        :param test_path:       Path to summary file, produced during pipeline test run.
        :param ref_path:        Path to reference summary file
        :return:                True if summaries are identical, False otherwise.
        """
        with open(test_path, "r") as test_file:
            test_lines = test_file.readlines()

        with open(ref_path, "r") as ref_file:
            ref_lines = ref_file.readlines()

        if len(test_lines) != len(ref_lines):
            return False

        for t, r in zip(test_lines, ref_lines):
            t_tokens = t.split()
            r_tokens = r.split()

            if len(t_tokens) != len(r_tokens):
                return False

            for tt, rr in zip(t_tokens, r_tokens):
                if tt.strip() != rr.strip():
                    return False

        return True

    @staticmethod
    def _print_text_file(path: str) -> None:
        """
        Print text file (text dash board) to stderr

        :param path:        Path to the file.
        :return:            None
        """
        with open(path, "r") as file:
            text = file.read()
            print(f"\n{path}:\n{text}", file=sys.stderr)

    @staticmethod
    def compare_summaries(test_path: str, ref_path: str):
        """
        Compare pipeline dash board summaries and print out both files in case of any differences.

        :param test_path:       Path to summary file, produced during pipeline test run.
        :param ref_path:        Path to reference summary file
        :return:                True if summaries are identical, False otherwise.
        """
        if not PipelineIntegrationTestCase._cmp_summaries(test_path, ref_path):
            PipelineIntegrationTestCase._print_text_file(test_path)
            PipelineIntegrationTestCase._print_text_file(ref_path)
            return False

        return True

    @staticmethod
    def prepare_test_dir(test_path: str, corpus_path: str) -> str:
        """
        Prepare pipeline test temporary directory:
            - create temporary directory;
            - copy all files from 'test_path' to the temporary directory;
            - create symbol link to a corpus file/directory

        :param test_path:       Path to a directory where test files reside.
        :param corpus_path:     Path to a corpus file or directory.
        :return:                Path to prepared test directory
        """
        if not os.path.isdir(test_path):
            raise FileNotFoundError(f"'{test_path}' does not exist.")

        if test_path.endswith("/"):
            test_path = test_path[:-1]

        last_slash_pos = test_path.rfind("/")
        test_dir_name = test_path if last_slash_pos < 0 else test_path[last_slash_pos+1:]
        path_to_create = "/var/tmp/" + test_dir_name

        # Remove temporary directory if it's already there
        if os.path.isdir(path_to_create):
            shutil.rmtree(path_to_create)

        # Copy directory pointed by 'test_path' to a new temporary directory
        shutil.copytree(test_path, path_to_create)

        pwd = os.environ["PWD"]

        if os.path.isfile(corpus_path):
            os.mkdir("data")
            os.symlink(f"{pwd}/{corpus_path}", path_to_create + f"/data/{os.path.split(corpus_path)[1]}")

        elif os.path.isdir(corpus_path):
            os.symlink(f"{pwd}/{corpus_path}", path_to_create + f"/data", True)

        else:
            raise FileNotFoundError("Corpus file/directory does not exist.")

        # Create 'dict' pseudo directory
        os.symlink(f"{pwd}/{DICT_REL_PATH}", path_to_create + f"/dict", True)

        return path_to_create

    def run_pipeline_test_case(self, test_name: str, corpus_path: str) -> None:
        """
        Execute pipeline integration test

        :param test_name:       Test test/subdirectory name.
        :param corpus_path:     Path to a corpus file/directory.
        :return:                None
        """
        test_path = f"{TESTS_ROOT}/{test_name}"

        tmp_test_path = self.prepare_test_dir(test_path, corpus_path)

        self.assertEqual(f"/var/tmp/{test_name}", tmp_test_path)
        self.assertTrue(os.path.isdir(tmp_test_path))

        # Run pipeline
        self.assertEqual(0, self.run_pipeline(f"{tmp_test_path}/{test_name}.json"),
                         f"Error executing pipeline. See '{tmp_test_path}/{test_name}.log' for details.")

        summary_path = f"{tmp_test_path}/{test_name}-summary.txt"
        reference_path = f"{tmp_test_path}/{test_name}-expected.txt"

        # Check if there is a summary file in the directory
        self.assertTrue(os.path.isfile(summary_path))

        # Compare summaries
        self.assertTrue(self.compare_summaries(reference_path, summary_path),
                        f"'{summary_path}' and '{reference_path}' mismatch.")

        # Remove temporary directory on success
        shutil.rmtree(tmp_test_path)
