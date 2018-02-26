#!/usr/bin/python
# coding=utf-8

# ASuMa, Feb 2018

import sys, getopt
import re

def main(argv):
	"""
		PreCleaner takes two mandatory arguments and several optional ones:

		"Usage: test.py -i <inputfile> -o <outputfile> [-c <chars_invalid>] [-s <suffixes>] [-l <sentence_length] [-t <token_length>] 
		[-x <sentence_symbols>] [-y <sentence_tokens>] [-z <token_symbols>] [-U] [-q]"

		inputfile 			Name of inputfile
		outputfile			Name of ouputfile
		[
		chars_invalid		characters to delete from text
		suffixes 			Suffixes to eliminate in text, need to come in a string, separated by spaces.
							For example, -s "'s 'd n't" would eliminate all suffixes 's, 'd, n't
							Of course, as suffixes, they need to come at the end of a word to be eliminated
		sentence_length		maximum sentence length accepted (sentences with more are deleted)
		token_length 		maximum token lenght accepted (tokens with more are deleted)
		sentences_symbols	symbols invalidating sentences
		sentence_tokens 	tokens invalidating sentences
		token_symbols 		symbols invalidating tokens
		-U 					flag to keep uppercase letters (default is to convert to lowercase)
		-q 					flag to keep quotes (default is to convert them to spaces)
		]
	"""
	inputfile = ''
	outputfile = ''
	invalid_chars = ""
	new_suffix_list = []
	max_tokens = 16
	max_chars = 25
	sentence_invalid_symbols = []
	sentence_invalid_tokens = []
	token_invalid_symbols = []
	convert_lowercase = True
	convert_quotes_to_spaces = True
	try:
		opts, args = getopt.getopt(argv,"hi:o:c:s:l:t:x:y:z:Uq",["ifile=",
			"ofile=", "chars_invalid=" "suffixes=", "sen_length=", 
			"token_length=", "sentence_symbols=", "sentence_tokens=", 
			"token_symbols=" "Uppercase", "quotes"])
	except getopt.GetoptError:
		print("Usage: test.py -i <inputfile> -o <outputfile> [-c <chars_invalid>] [-s <suffixes>] [-l <sentence_length] [-t <token_length>] [-x <sentence_symbols>] [-y <sentence_tokens>] [-z <token_symbols>] [-U] [-q]")
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'Usage: test.py -i <inputfile> -o <outputfile>'
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
		elif opt in ("-c", "--chars_invalid"):
			invalid_chars = arg
		elif opt in ("-s", "--suffixes"):
			suffix_list = arg.split()
			new_suffix_list = Prepare_Suffix_List(suffix_list)
		elif opt in ("-l", "--sen_length"):
			max_tokens = int(arg)
		elif opt in ("-t", "--token_length"):
			max_chars = int(arg)
		elif opt in ("-x", "--sentence_symbols"):
			sentence_invalid_symbols = arg
		elif opt in ("-y", "--sentence_tokens"):
			sentence_invalid_tokens = arg.split()
		elif opt in ("-z", "--token_symbols"):
			token_invalid_symbols = arg
		elif opt in ("-U", "--Uppercase"):
			convert_lowercase = False
		elif opt in ("-q", "--quotes"):
			convert_quotes_to_spaces = False

	sentences = Load_Files(inputfile)

	fo = open(outputfile, "w")
	for sentence in sentences:
		temp_sentence = Normalize_Sentence(sentence, convert_quotes_to_spaces)
		temp_sentence = Remove_Suffixes(temp_sentence, new_suffix_list)
		tokenized_sentence = Naive_Tokenizer(temp_sentence)
		if Ignore_Long_Sentence(tokenized_sentence, max_tokens) == True:
			continue
		tokenized_sentence = Remove_Long_Tokens(tokenized_sentence, max_chars)
		if Ignore_Invalid_Sentence(tokenized_sentence, sentence_invalid_symbols, sentence_invalid_tokens) == True:
			continue
		tokenized_sentence = Remove_Invalid_Tokens(tokenized_sentence, token_invalid_symbols)
		final_sentence = " ".join(tokenized_sentence) + "\n"
		final_sentence = Clean_Sentence(final_sentence, invalid_chars)
		if convert_lowercase == True:
			final_sentence = final_sentence.lower()
		Write_Output_Sentence(fo, final_sentence)
	fo.close()

def Load_Files(filename):
	"""
		Loads file already sentence-splitted, returning a list of all sentences
	"""
	file = open(filename, "r")
	sentences = file.readlines()
	file.close()
	return sentences

def Write_Output_Sentence(fo, sentence):
	"""
		writes sentence to the output file
	"""
	fo.write(sentence)

def Remove_Caps(sentence):
    """
        Converts all capital letters in "data" into small caps
    """
    return sentence.lower()

def Naive_Tokenizer(sentence):
	"""
		Tokenizes sentence, naively splitting by space only.
		This is only for cleaning, a real tokenizer is suppossed to be applied
		later in the process.
	"""
	return sentence.split()

def Remove_Long_Tokens(tokenized_sentence, max_chars):
	"""
		Removes token from tokenized_sentence if token is longer than max_word_length
	"""
	short_word_sentence = [] + tokenized_sentence # forcing a copy, avoid pass by reference
	for token in tokenized_sentence:
		if len(token) > max_chars:
			short_word_sentence.remove(token)

	return short_word_sentence

def Ignore_Long_Sentence(tokenized_sentence, max_tokens):
	"""
		Determines if tokenized_sentence should be ignored, if it has more than max_tokens
	"""
	if len(tokenized_sentence) > max_tokens:
		return True
	else:
		return False

def Remove_Invalid_Tokens(tokenized_sentence, invalidating_symbols):
	"""
		Returns a tokenized sentence without tokens that include invalidating_symbols
	"""
	valid_tokens_sentence = [] + tokenized_sentence # forcing a copy, avoid pass by reference
	for token in tokenized_sentence:
		for invalid_symbol in invalidating_symbols:
			if invalid_symbol in token:
				valid_tokens_sentence.remove(token)

	return valid_tokens_sentence

def Ignore_Invalid_Sentence(tokenized_sentence, invalidating_symbols, invalidating_tokens):
	"""
		Determines if tokenized_sentence should be ignored, 
		if it contains invalidating_tokens or invalidating_symbols 
	"""
	for token in tokenized_sentence:
		if token in invalidating_tokens:
			print("ignora")
			return True
	dummy = Remove_Invalid_Tokens(tokenized_sentence, invalidating_symbols)	
	if len(dummy) < len(tokenized_sentence):
		return True

	return False

def Clean_Sentence(sentence, invalid_chars):
	"""
		Cleans sentence from invalid chars
	"""
	return sentence.translate(None, invalid_chars)#translate_table)

def Normalize_Sentence(sentence, convert_quotes_to_spaces):
	"""
		Converts all different apostrophes, double quotes and dashes to standard symbols
	"""

	# Normalize apostrophes, dashes and quotes obtained from Wikipedia Apostrophe page
	sentence = re.sub(r"[\`]|’", "'", sentence)
	sentence = re.sub(r"-{2,}|‒|–|—|―|‐|-|−", "-", sentence) # some dashes look the same, but they are apparently different
	sentence = re.sub(r"\'\'|“|”", '\\"', sentence)
	if convert_quotes_to_spaces == True:
		sentence = re.sub(r'\\"|"', " ", sentence) # sentence splitter escapes double quotes, as apparently needed by guile
	return sentence

def Prepare_Suffix_List(suffix_list):
	"""
		Adds regular expression parts to given suffixes
	"""
	new_suffix_list = []
	for suffix in suffix_list:
		regex_suffix = r"(?<=\w)" + suffix + r"(?=\s)"
		new_suffix_list = new_suffix_list + [regex_suffix]
	return new_suffix_list


def Remove_Suffixes(sentence, suffix_list):
	"""
		Removes suffixes in the list from the sentence
	"""
	for suffix in suffix_list:
		sentence = re.sub(suffix, "", sentence)
	return sentence

if __name__ == "__main__":
	main(sys.argv[1:])