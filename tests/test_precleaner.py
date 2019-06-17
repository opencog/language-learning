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

	def test_Forbidden_Symbols(self):
		invalid_chars = 'aeiou'
		sentence = "This is a normal sentence"
		sentence_ref = "Ths s  nrml sntnc"
		self.assertEqual(sentence_ref, Clean_Sentence(sentence, invalid_chars, []))

	def test_Boundary_Chars(self):
		boundary_chars = 'aeiou'
		sentence = "This is unusual for a sentence"
		sentence_ref = "This  i s  u nusual for  a  sentenc e"
		self.assertEqual(sentence_ref, Char_Tokenizer(sentence, boundary_chars, ""))

		boundary_chars = u"\"'."
		sentence2 = "We're testin' another. \"sentence\"."
		sentence2_ref = "We're testin ' another .  \" sentence\" ."
		#self.assertEqual(sentence2_ref, Char_Tokenizer(sentence2, boundary_chars, ""))

	def test_Splitter_Symbols(self):
		sentence = "This_is a t*est sen—tence—."
		sentence_ref = "This is a t est sen tence ."
		self.assertEqual(sentence_ref, Clean_Sentence(sentence, "", []))

	def test_Tokenized_Chars(self):
		tokenized_chars = ".?!"
		sentence = "A.test! sentence?."
		sentence_ref = "A . test !  sentence ?  . "
		self.assertEqual(sentence_ref, Char_Tokenizer(sentence, "", tokenized_chars))

	def test_Remove_Invalid_Tokens(self):
		invalid_token_symbols = "ai"
		tok_list = ["This", "is", "a", "test", "sentence"]
		tok_list_ref = ["test", "sentence"]
		self.assertEqual(tok_list_ref, Remove_Invalid_Tokens(tok_list, invalid_token_symbols))

	def test_Symbol_Invalidate_Sentence(self):
		invalid_sent_symbols = "a$"
		tok_list = ["This", "is", "a", "test", "sentence"]
		tok_list2 = ["Shorter", "test", "sentence"]
		self.assertTrue(Ignore_Invalid_Sentence(tok_list, invalid_sent_symbols, []))
		self.assertTrue(not Ignore_Invalid_Sentence(tok_list2, invalid_sent_symbols, []))

	def test_Token_Invalidate_Sentence(self):
		invalid_sent_tokens = ["is", "evil"]
		tok_list = ["This", "is", "a", "test", "sentence"]
		tok_list2 = ["This", "is", "an", "evil", "test", "sentence"]
		tok_list3 = ["Innocent", "sentence"]
		self.assertTrue(Ignore_Invalid_Sentence(tok_list, "", invalid_sent_tokens))
		self.assertTrue(Ignore_Invalid_Sentence(tok_list2, "", invalid_sent_tokens))
		self.assertTrue(not Ignore_Invalid_Sentence(tok_list3, "", invalid_sent_tokens))

	def test_Substitute_Numbers(self):
		num_test1 = "Those 3 dogs ate -4.1 hot dogs"
		num_test1_ref = "Those @number@ dogs ate @number@ hot dogs"
		self.assertEqual(Substitute_Numbers(num_test1), num_test1_ref)
		num_test2 = "Adding 0,000,000 to 17;311.13 is -useless"
		num_test2_ref = "Adding @number@ to @number@ is -useless"
		self.assertEqual(Substitute_Numbers(num_test2), num_test2_ref)
		num_test3 = "Notatio.n: -51,123123 and 884'432'211 are 3cky"
		num_test3_ref = "Notatio.n: @number@ and @number@ are 3cky"
		self.assertEqual(Substitute_Numbers(num_test3), num_test3_ref)

	def test_Substitute_Dates(self):
		date_test1 = "On 5/13, meaning 5/13/2018, also written as 2018/5/13."
		date_test1_ref = "On  @date@ , meaning  @date@ , also written as  @date@ ."
		self.assertEqual(Substitute_Dates(date_test1), date_test1_ref)
		date_test2 = "Can't write as 5/2018/13, but 18-5-13 or 13.5.18"
		date_test2_ref = "Can't write as 5/2018/13, but  @date@  or  @date@ "
		self.assertEqual(Substitute_Dates(date_test2), date_test2_ref)
		date_test3 = "Try May 2018, or May 2018, specifically May 13th, 2018."
		date_test3_ref = "Try  @date@ , or  @date@ , specifically  @date@ ."
		self.assertEqual(Substitute_Dates(date_test3), date_test3_ref)
		date_test4 = "It was May-05-2018. Or 2018-May-13, but not 2018-XXX-13"
		date_test4_ref = "It was  @date@ . Or  @date@ , but not 2018-XXX-13"
		self.assertEqual(Substitute_Dates(date_test4), date_test4_ref)


if __name__ == '__main__':
	unittest.main()