import unittest
import sys
from src.link_grammar.evaluate import Load_File, Get_Parses, MakeSets, Evaluate_Parses


parse_no_wall = """tuna isa fish . 
0 tuna 1 isa
1 isa 2 fish
2 fish 3 .
"""

parse_with_wall = """tuna isa fish . 
0 ###LEFT-WALL### 1 tuna
1 tuna 2 isa
2 isa 3 fish
3 fish 4 .
"""

# parse_with_wall = """tuna isa fish .
# 0 ###LEFT-WALL### 1 tuna
# 1 tuna 2 isa
# 2 isa 3 fish
# 3 fish 4 .
# """

class TestEvalMethods(unittest.TestCase):

    def test_Get_Parses(self):
        # no_wall_parses = Get_Parses(parse_no_wall)
        # with_wall_parses = Get_Parses(parse_with_wall)
        # print(with_wall_parses, file=sys.stderr)
        ref_data = Load_File("test-data/parses/poc-turtle-mst/one-parse-expected.txt")
        # test_data = Load_File("test-data/parses/poc-turtle-mst/one-parse-expected.txt")
        test_data = Load_File("test-data/parses/poc-turtle-mst/one-parse-no-wall.txt")
        print("ref_data='", ref_data, "'", file=sys.stderr)
        print("test_data='", test_data, "'", file=sys.stderr)
        ref_parses = Get_Parses(ref_data, True)
        test_parses = Get_Parses(test_data, True)

        self.assertEqual(ref_parses, test_parses)

        # Evaluate_Parses(test_parses, ref_parses, False, True, sys.stderr)

if __name__ == '__main__':
    unittest.main()