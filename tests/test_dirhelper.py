import unittest

from src.common.dirhelper import *


class DirHelperTestCase(unittest.TestCase):

    def test_traverse_dir_tree_err_no_callback(self):
        """ Test 'No callback' exception"""
        with self.assertRaises(ValueError) as ctx:
            traverse_dir_tree("./test-data", "")

        self.assertEqual("No callback arguments specified.", str(ctx.exception))

    # @unittest.skip
    def test_traverse_dir_tree_err_empty_list1(self):
        """ Test for empty file argument list """
        with self.assertRaises(ValueError) as ctx:
            traverse_dir_tree("./test-data", "", [])

        self.assertEqual("Empty argument list for 'file_arg_list'.", str(ctx.exception))

    # @unittest.skip
    def test_traverse_dir_tree_err_empty_list2(self):
        """ Test for empty directory argument list """
        with self.assertRaises(ValueError) as ctx:
            traverse_dir_tree("./test-data", "", None, [])

        self.assertEqual("Empty argument list for 'dir_arg_list'.", str(ctx.exception))

    # @unittest.skip
    def test_traverse_dir_tree_err_1st_arg_not_callable_in_filecb(self):
        """ Test for non callable argument (on_file)"""
        with self.assertRaises(ValueError) as ctx:
            traverse_dir_tree("./test-data", "", ["dummy"])

        self.assertEqual("The argument you specified in 'file_arg_list[0]' field is not callable.", str(ctx.exception))

    # @unittest.skip
    def test_traverse_dir_tree_err_1st_arg_not_callable_in_dircb(self):
        """ Test for non callable argument (on_directory)"""
        with self.assertRaises(ValueError) as ctx:
            traverse_dir_tree("./test-data", "", None, ["dummy"])

        self.assertEqual("The argument you specified in 'dir_arg_list[0]' field is not callable.", str(ctx.exception))

    def test_traverse_dir_tree(self):
        """ Test traverse process """
        def on_file(file: str, args: list):
            # dir_list = file[len(args[0])+1:].split(r"/")
            dir_list = file.split(r"/")
            # print(dir_list[-4:-1], args)
            print(dir_list[-2], args)

        def on_dir(dir: str, args: list) -> bool:
            # print("on_dir(): " + str(len(dir[len(args[0])+1:].split("/"))) + "\t" + dir[len(args[0])+1:])
            return True

        root = "tests/test-data/parses/AGI-2018-paper-data-2018-04-22"

        # traverse_dir_tree(root, ".dict", [on_file, root], None, True)
        traverse_dir_tree(root, ".dict", None, [on_dir, root], True)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
