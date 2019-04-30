import sys
import unittest
from src.pipeline.varhelper import get_variable_value, get_referenced_variable_value, subst_all_vars_in_str, subst_variables_in_dict2

scopes = {
    "THIS": {"row": 1, "row_of": 2, "row_of_the_table": 3, "LEAF": "path/to/child"},
    "PREV": {"row": 4, "row_of": 5, "row_of_the_table": 6, "LEAF": "path/to/parent"}
}


class VarhelperTestCase(unittest.TestCase):

    def test_subst_all_vars_in_str(self):
        self.assertEqual(4, subst_all_vars_in_str("%PREV.row", scopes))

    def test_get_variable_value(self):
        key, value, cls = get_variable_value("row_of_the_table", {"row": 1, "row_of": 2, "row_of_the_table": 3})
        self.assertEqual(("row_of_the_table", 3, "int"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_unreferenced(self):
        key, value, cls = get_referenced_variable_value("PREV", scopes)

        self.assertEqual(("PREV", "path/to/parent", "str"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_leaf(self):
        key, value, cls = get_referenced_variable_value("LEAF", scopes)

        self.assertEqual(("LEAF", "path/to/child", "str"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_partial1(self):
        key, value, cls = get_referenced_variable_value("PREV/some_folder", scopes)

        self.assertEqual(("PREV", "path/to/parent", "str"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_partial2(self):
        key, value, cls = get_referenced_variable_value("PREV.row/some_folder", scopes)

        self.assertEqual(("PREV.row", 4, "int"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_partial3(self):
        key, value, cls = get_referenced_variable_value("row/some_folder", scopes)

        self.assertEqual(("row", 1, "int"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_1(self):
        key, value, cls = get_referenced_variable_value("PREV.row_of_the_table", scopes)

        self.assertEqual(("PREV.row_of_the_table", 6, "int"), (key, value, cls.__name__))

    # @unittest.skip
    def test_get_referenced_variable_value_2(self):
        key, value, cls = get_referenced_variable_value("PREV.row_of", scopes)

        self.assertEqual(("PREV.row_of", 5, "int"), (key, value, cls.__name__))

    def test_subst_all_vars_in_str_1(self):
        self.assertEqual("path/to/parent/1", subst_all_vars_in_str("%PREV/%row", scopes))

    # @unittest.skip
    def test_subst_all_vars_in_str_2(self):
        self.assertEqual("path/to/parent/4", subst_all_vars_in_str("%PREV/%PREV.row", scopes))

    def test_subst_all_vars_in_str_3(self):
        self.assertTrue("/var/tmp/path/to/parent/1", subst_all_vars_in_str("/var/tmp/%PREV/%row", scopes))

    def test_subst_variables_in_dict2(self):
        self.assertEqual({"x": "1 + 4", "y": "/var/tmp/1"},
                         subst_variables_in_dict2({"x": "1 + %PREV.row", "y": "/var/tmp/%row"}, scopes))
        self.assertEqual({"x": "4 + 1", "y": "/var/tmp/1"},
                         subst_variables_in_dict2({"x": "%PREV.row + 1", "y": "/var/tmp/%row"}, scopes))

    def test_subst_variables_in_dict2_nested(self):
        self.assertEqual({"SCOPE": {"x": "1 + 4", "y": "/var/tmp/1"}},
                         subst_variables_in_dict2({"SCOPE": {"x": "1 + %PREV.row", "y": "/var/tmp/%row"}}, scopes))

    def test_subst_variables_in_dict2_not_nested(self):
        self.assertEqual({"SCOPE": {"x": "1 + %PREV.row", "y": "/var/tmp/%row"}},
                         subst_variables_in_dict2({"SCOPE": {"x": "1 + %PREV.row", "y": "/var/tmp/%row"}},
                                                  scopes, False))


if __name__ == '__main__':
    unittest.main()
