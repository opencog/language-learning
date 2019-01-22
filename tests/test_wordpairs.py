import unittest
from src.grammar_tester.wordpairs import WordPair, WordPairs

class WordPairsTestCase(unittest.TestCase):

    def setUp(self):
        self.lcase_pairs = WordPairs()

    def test_key(self):
        self.assertEqual("i^^^see", self.lcase_pairs._key("I", "See"))

    def test_add(self):
        self.lcase_pairs.add("I", "see")

        self.assertEqual(1, len(self.lcase_pairs._pairs))
        self.assertEqual(1, len(self.lcase_pairs._left))
        self.assertEqual(1, len(self.lcase_pairs._right))
        self.assertEqual(2, self.lcase_pairs._word_count)

        self.lcase_pairs.add("You", "see")

        pair = self.lcase_pairs._pairs[self.lcase_pairs._key("you", "see")]

        self.assertEqual("you", pair.left)
        self.assertEqual("see", pair.right)

        self.assertEqual(2, len(self.lcase_pairs._pairs))
        self.assertEqual(2, len(self.lcase_pairs._left))
        self.assertEqual(1, len(self.lcase_pairs._right))
        self.assertEqual(3, self.lcase_pairs._word_count)

        self.assertEqual(0.5, self.lcase_pairs._left_probability("i"))
        self.assertEqual(1.0, self.lcase_pairs._right_probability("see"))

        left_count, right_count = 0, 0

        for num in self.lcase_pairs._left.values():
            left_count += num

        self.assertEqual(left_count, self.lcase_pairs._left_count)

        for num in self.lcase_pairs._right.values():
            right_count += num

        self.assertEqual(right_count, self.lcase_pairs._right_count)

        self.assertEqual(0.5, self.lcase_pairs._pair_probability(self.lcase_pairs._key("i", "see")))

        # print(self.lcase_pairs._pair_mutual_info(self.lcase_pairs._key("i", "see")))


if __name__ == '__main__':
    unittest.main()
