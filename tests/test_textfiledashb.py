import unittest
import os
from decimal import Decimal

from src.grammar_tester.textfiledashb import TextFileDashboardConf, DashboardError
from src.common.fileconfman import JsonFileConfigManager
from src.common.parsemetrics import ParseMetrics, ParseQuality


class TextFileDashTestCase(unittest.TestCase):

    def setUp(self):
        conf_path = "tests/test-data/config/AGI-2018.json"
        cfg_man = JsonFileConfigManager(conf_path)
        self.dboard = TextFileDashboardConf(cfg_man)

    def test_init(self):
        """ Test constructor """
        self.assertTrue(hasattr(self.dboard, "_path"))
        self.assertTrue(hasattr(self.dboard, "_row_count"))
        self.assertTrue(hasattr(self.dboard, "_col_count"))
        self.assertTrue(hasattr(self.dboard, "_dashboard"))
        self.assertTrue(hasattr(self.dboard, "_config"))
        self.assertEqual(18, len(self.dboard._dashboard))

        for row in self.dboard._dashboard:
            self.assertEqual(10, len(row))

    def test_on_statistics(self):
        """ Test callback method """
        pm, pq = ParseMetrics(), ParseQuality()

        pm.sentences, pq.sentences = 10, 10

        pm.average_parsed_ratio = Decimal("0.6")
        pq.quality = Decimal("0.4")

        self.dboard.on_statistics(["connectors-DRK-connectors", "LG_ANY_all_parses",
                                   "POC-English-NoAmb-LEFT-WALL+period"], pm, pq)


    def test_set_cell_by_indexes(self):
        """ Test setting cell values """
        self.dboard.set_cell_by_indexes(0, 0, "00")
        self.dboard.set_cell_by_indexes(0, 1, "01")
        self.dboard.set_cell_by_indexes(1, 0, "10")
        self.dboard.set_cell_by_indexes(1, 1, "11")

        with self.assertRaises(IndexError) as ctx:
            self.dboard.set_cell_by_indexes(40, 50, "45")

        self.assertEqual("list index out of range", str(ctx.exception))

    @unittest.skip
    def test_set_row_names(self):
        """ Test setting row names """
        self.dboard.set_row_names(["1", "2"])
        self.assertTrue(hasattr(self.dboard, "_row_names"))
        self.assertEqual(2, len(self.dboard._row_names))

    def test_set_row_names_exception(self):
        """ Test row names list size mismatch exception """
        with self.assertRaises(ValueError) as ctx:
            self.dboard.set_row_names(["1", "2", "3"])

        self.assertEqual("'names' list size does not match the number of rows allocated", str(ctx.exception))

    @unittest.skip
    def test_set_col_names(self):
        """ Test setting column names """
        self.dboard.set_col_names(["A", "B"])
        self.assertTrue(hasattr(self.dboard, "_col_names"))
        self.assertEqual(2, len(self.dboard._col_names))

    def test_set_col_names_exception(self):
        """ Test column names list size mismatch exception """
        with self.assertRaises(ValueError) as ctx:
            self.dboard.set_col_names(["A", "B", "C"])

        self.assertEqual("'names' list size does not match the number of columns allocated", str(ctx.exception))

    def test_get_row_index_not_set_exception(self):
        """ Test row names unset exception """
        with self.assertRaises(DashboardError) as ctx:
            index = self.dboard._get_row_index("1")

        self.assertEqual("row names are not set", str(ctx.exception))

    @unittest.skip
    def test_get_row_index(self):
        """ Test getting row indexes """
        self.dboard.set_row_names(["1", "2"])
        self.assertEqual(0, self.dboard._get_row_index("1"))
        self.assertEqual(1, self.dboard._get_row_index("2"))

    def test_get_col_index_not_set_exception(self):
        """ Test for unset column names exception """
        with self.assertRaises(DashboardError) as ctx:
            index = self.dboard._get_col_index("A")

        self.assertEqual("column names are not set", str(ctx.exception))

    @unittest.skip
    def test_get_col_index(self):
        """ Test getting column indexes """
        self.dboard.set_col_names(["A", "B"])
        self.assertEqual(0, self.dboard._get_col_index("A"))
        self.assertEqual(1, self.dboard._get_col_index("B"))

    # @unittest.skip
    def test_update_dashboard(self):
        """ Test saving dashboard data to a file """
        os.unlink(self.dboard._path)
        self.dboard.update_dashboard()
        self.assertTrue(os.path.isfile(self.dboard._path))


if __name__ == '__main__':
    unittest.main()
