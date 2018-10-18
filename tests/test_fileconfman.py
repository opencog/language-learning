import unittest
import os, sys
from decimal import Decimal

from src.common.fileconfman import JsonFileConfigManager
from src.common.parsemetrics import ParseMetrics

conf_path = "tests/test-data/config/config-example-01.json"

params = \
      {
        "input_grammar": "./grammar.dict",
        "input_categories": "./cat_tree.txt",
        "parse_format": "ull"
      }

class JsonRWTestCase(unittest.TestCase):

    def test_string_keys(self):
        """ Argument format string test """
        nodes = ["AFC", "BZ"]
        # print(nodes)
        # print(tuple(nodes))

        self.assertEqual("AFCBZ", "{0[0]}{0[1]}".format(nodes))
        self.assertEqual("BZ--AFC", "{1}--{0}".format(*nodes))

        pm = ParseMetrics()
        pm.average_parsed_ratio = Decimal("0.66")
        pm.sentences = 3

        self.assertEqual("3>>3>>22.00%", "{sentences}>>{sentences}>>{parseability}".format(parseability=pm.parseability_str(pm).strip(), sentences=pm.sentences))
        self.assertEqual("CBA", "{nodes[2]}{nodes[1]}{nodes[0]}".format(nodes=["A", "B", "C"]))
        self.assertEqual("B>>3>>22.00%", "{nodes[1]}>>{sentences}>>{parseability}".format(parseability=pm.parseability_str(pm).strip(), sentences=pm.sentences, nodes=["A", "B", "C"]))

    # @unittest.skip
    def test_read_config(self):
        """ Configuration read test """
        cm = JsonFileConfigManager(conf_path)

        cfg = cm.get_config("", "grammar-tester")
        self.assertEqual(params, cfg[0])


if __name__ == '__main__':
    unittest.main()
