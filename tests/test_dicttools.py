import unittest
from src.link_grammar.dicttools import *


class LGDictToolsTestCase(unittest.TestCase):

    def test_init(self):
        # tuna isa fish
        rule_list = [
            DictRule("AAA", '"tuna"', "(AAABBB+)"),
            DictRule("BBB", '"isa"', "(AAABBB- & BBBCCC+)"),
            DictRule("CCC", '"fish"', "(BBBCCC-)")
        ]
        space: LGDictionaryRuleSpace = LGDictionaryRuleSpace(rule_list)

        self.assertEqual(sorted(space._word_rules.keys()), ["fish", "isa", "tuna"])
        self.assertEqual(sorted(space._word_rules["tuna"]),[ 0 ])
        self.assertEqual(sorted(space._word_rules["fish"]),[ 2 ])
        self.assertEqual(sorted(space._word_rules["isa"]), [ 1 ])

    def test_get_word_list(self):
        # tuna isa fish
        # parrot isa bird
        rule_list = [
            DictRule("AAA", '"tuna" "parrot"', "(AAABBB+)"),
            DictRule("BBB", '"isa"', "(AAABBB- & BBBCCC+)"),
            DictRule("CCC", '"fish" "bird"', "(BBBCCC-)")
        ]

        self.assertEqual(rule_list[0].get_word_list(), ["tuna", "parrot"])
        self.assertEqual(rule_list[1].get_word_list(), ["isa"])
        self.assertEqual(rule_list[2].get_word_list(), ["fish", "bird"])

    def test_get_disjunct_list(self):

        rule: DictRule = DictRule("AAA", '"tuna"', "(AAABBB+) or (BBBCCC- & AAACCC+)")

        self.assertEqual(rule.get_disjunct_list(), ["AAABBB+", "BBBCCC- & AAACCC+"])


if __name__ == '__main__':
    unittest.main()
