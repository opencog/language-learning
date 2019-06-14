# !/usr/bin/env python3
import os, sys
import unittest

module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path: sys.path.append(module_path)
from src.pre_cleaner.pre_cleaner import *

class PreCleanerTestCase(unittest.TestCase):

	def test_Remove_Caps(self):
		caps_sent1 = "Some CAPitalizEd letterS."
		lower_sent1 = "some capitalized letters."

		test_sent = Remove_Caps(caps_sent1)
		self.assertEqual(lower_sent1, test_sent)

	def test_Remove_Long_Tokens(self):
		max_chars = 5
		token_list = ["a" * (max_chars - 1), "a" * max_chars, "a" * (max_chars + 1)]
		cleaned_list = ["a" * (max_chars - 1), "a" * max_chars]

		self.assertEqual(Remove_Long_Tokens(token_list, max_chars), cleaned_list)

	def test_Ignore_Long_Sentence(self):
		max_tokens = 5
		list_short = list(range(max_tokens - 1))
		list_exact = list(range(max_tokens))
		list_long = list(range(max_tokens + 1))

		self.assertTrue(not Ignore_Long_Sentence(list_short, max_tokens))
		self.assertTrue(not Ignore_Long_Sentence(list_exact, max_tokens))
		self.assertTrue(Ignore_Long_Sentence(list_long, max_tokens))

	def test_Normalize_Tokens(self):
		apostrophes = "` ’ ‘" # different types of apostrophes
		apostrophes_ref = "' ' '"
		self.assertEqual(apostrophes_ref, Normalize_Sentence(apostrophes, False))

		dashes = "‑ ‐" # different types of dashes
		dashes_ref = "- -"
		self.assertEqual(dashes_ref, Normalize_Sentence(dashes, False))

		long_dashes = "-- ---- ― — – ‒" # different types of long dashes
		long_dashes_ref = "— — — — — —"
		self.assertEqual(long_dashes_ref, Normalize_Sentence(long_dashes, False))

		double_quotes = "'' “ ”" # different types of double quotes
		double_quotes_ref = '" " "'
		self.assertEqual(double_quotes_ref, Normalize_Sentence(double_quotes, False))

		mixed = "“ ’ ‐ ‑‑ ``" # Assortment of the above
		mixed_ref = '" \' - — "'
		self.assertEqual(mixed_ref, Normalize_Sentence(mixed, False))


if __name__ == '__main__':
	unittest.main()