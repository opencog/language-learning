import os
import sys
import shutil
import unittest
from subprocess import PIPE, Popen
from typing import Union, Tuple, List

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
    def _compare_text_files(test_path: str, ref_path: str) -> bool:
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
    def compare_text_files(test_path: str, ref_path: str):
        """
        Compare pipeline dash board summaries and print out both files in case of any differences.

        :param test_path:       Path to summary file, produced during pipeline test run.
        :param ref_path:        Path to reference summary file
        :return:                True if summaries are identical, False otherwise.
        """
        if not PipelineIntegrationTestCase._compare_text_files(test_path, ref_path):
            PipelineIntegrationTestCase._print_text_file(test_path)
            PipelineIntegrationTestCase._print_text_file(ref_path)
            return False

        return True

    @staticmethod
    def create_sym_link(data_path: str, root: str, name: str = "data"):
        """
        Create symbolic link for given file or directory

        :param data_path:       Path to a file or directory.
        :param root:            Root path where symbolic link is to be created.
        :param name:            Name of the symbolic link to be created.
        :return:
        """
        pwd = os.environ["PWD"]

        if os.path.isfile(data_path):
            os.mkdir(f"{root}/{name}")
            os.symlink(f"{pwd}/{data_path}", f"{root}/{name}/{os.path.split(data_path)[1]}")

        elif os.path.isdir(data_path):
            os.symlink(f"{pwd}/{data_path}", f"{root}/{name}", True)

        else:
            raise FileNotFoundError("Corpus file/directory does not exist.")

    @staticmethod
    def prepare_test(test_path: str, data_path: Union[str, List[Tuple[str, str]]]) -> str:
        """
        Prepare pipeline test temporary directory:
            - create temporary directory;
            - copy all files from 'test_path' to the temporary directory;
            - create symbol link to a corpus file/directory

        :param test_path:       Path to a directory where test files reside.
        :param data_path:       Path to a corpus file or directory/List of tuples (path, link_name).
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

        if isinstance(data_path, str):
            PipelineIntegrationTestCase.create_sym_link(data_path, path_to_create)

        elif isinstance(data_path, list):
            for entry in data_path:
                PipelineIntegrationTestCase.create_sym_link(entry[0], path_to_create, entry[1])

        # Create 'dict' pseudo directory
        os.symlink(f"{pwd}/{DICT_REL_PATH}", path_to_create + f"/dict", True)

        return path_to_create

    def check_expectations(self, tmp_test_path: str):
        """
        Compare all files ending with ".expected" suffix with their respective counterparts

        :param tmp_test_path:   Path to test directory
        :return:                None
        """
        for file_path in os.listdir(tmp_test_path):
            if file_path.endswith(".expected"):
                test_path = f"{tmp_test_path}/{file_path[:-9]}"
                ref_path = f"{tmp_test_path}/{file_path}"

                # Check if there is a summary file in the directory
                self.assertTrue(os.path.isfile(test_path))

                # Compare summaries
                self.assertTrue(self.compare_text_files(ref_path, test_path),
                                f"'{test_path}' and '{ref_path}' mismatch.")

    def run_pipeline_test_case(self, test_name: str, data_path: Union[str, List[Tuple[str, str]]]) -> None:
        """
        Execute pipeline integration test

        :param test_name:       Test test/subdirectory name.
        :param corpus_path:     Path to a corpus file/directory.
        :return:                None
        """
        test_path = f"{TESTS_ROOT}/{test_name}"

        tmp_test_path = self.prepare_test(test_path, data_path)
        # tmp_test_path = self.prepare_test_dir(test_path, corpus_path)

        self.assertEqual(f"/var/tmp/{test_name}", tmp_test_path)
        self.assertTrue(os.path.isdir(tmp_test_path))

        # Run pipeline
        self.assertEqual(0, self.run_pipeline(f"{tmp_test_path}/{test_name}.json"),
                         f"Error executing pipeline. See '{tmp_test_path}/{test_name}.log' for details.")

        # Compare all expected files with their respective test results
        self.check_expectations(tmp_test_path)

        # Remove temporary directory on success
        shutil.rmtree(tmp_test_path)
