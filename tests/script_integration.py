import os
import sys
import shutil
import unittest
from subprocess import PIPE, Popen
from typing import Optional


class ScriptIntegrationTestCase(unittest.TestCase):
    """
    General CLI script integration test

    """
    @staticmethod
    def run_script(cmd_line: str, output_path: Optional[str]):
        """
        Run CLI script

        :param cmd_line:        Command line including name of the script and all arguments.
        :param output_path:     File path to save 'stdout' output to.
        :return:                OS error level.
        """
        arg_list = cmd_line.split()

        cmd = shutil.which(arg_list[0])

        if cmd is None:
            raise FileNotFoundError(f"'{cmd}' is not found.")

        # print(cmd, file=sys.stderr)

        with Popen([cmd, *arg_list[1:]], stdout=PIPE) as proc:
            raw, err = proc.communicate()

            if output_path is not None:
                with open(output_path, "w") as out_file:
                    out_file.write(raw.decode("utf-8-sig"))

            ret_code = proc.returncode

        return ret_code

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
            os.mkdir(path_to_create + "/data")
            os.symlink(f"{pwd}/{corpus_path}", path_to_create + f"/data/{os.path.split(corpus_path)[1]}")

        elif os.path.isdir(corpus_path):
            os.symlink(f"{pwd}/{corpus_path}", path_to_create + f"/data", True)

        # else:
        #     raise FileNotFoundError("Corpus file/directory does not exist.")
        #
        # # Create 'dict' pseudo directory
        # os.symlink(f"{pwd}/{DICT_REL_PATH}", path_to_create + f"/dict", True)

        return path_to_create

    @staticmethod
    def compare_text_files(test_path: str, ref_path: str) -> bool:
        """
        Compare text files

        :param test_path:       Path to test file, produced during the script run.
        :param ref_path:        Path to reference file.
        :return:                True if files are identical, False otherwise.
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
