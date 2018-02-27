#!/usr/bin/python
# encoding: utf-8

# ASuMa, Feb 2018

import sys, getopt
import re
from HTMLParser import HTMLParser

def main(argv):
	"""
		PreCleaner takes two mandatory arguments and several optional ones:

		"Usage: test.py -i <inputfile> -o <outputfile> [-c <chars_invalid>] [-s <suffixes>] [-l <sentence_length] [-t <token_length>] 
		[-x <sentence_symbols>] [-y <sentence_tokens>] [-z <token_symbols>] [-U] [-q] [-n] [-d] [-T] [-H] [-e]"

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
		-n 					keep numbers (default converts them to number_was_here token)
		-d 					keep dates (default converts them to date_was_here token)
		-T 					keep times (default converts them to time_was_here token)
		-H 					keep hyperlinks (default converts them to link_was_here token)
		-e 					keep escaped HTML and UniCode symbols (default decodes them)
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
	convert_numbers_to_tokens = True
	convert_dates_to_tokens = True
	convert_times_to_tokens = True
	convert_links_to_tokens = True
	decode_escaped = True
	try:
		opts, args = getopt.getopt(argv,"hi:o:c:s:l:t:x:y:z:UqndTHe",["ifile=",
			"ofile=", "chars_invalid=" "suffixes=", "sen_length=", 
			"token_length=", "sentence_symbols=", "sentence_tokens=", 
			"token_symbols=" "Uppercase", "quotes", "numbers", "dates", 
			"Times", "Hyperlinks", "escaped"])
	except getopt.GetoptError:
		print '''Usage: test.py -i <inputfile> -o <outputfile> 
		    [-c <chars_invalid>] [-s <suffixes>] [-l <sentence_length] 
		    [-t <token_length>] [-x <sentence_symbols>] [-y <sentence_tokens>]
		    [-z <token_symbols>] [-U] [-q] [-n] [-d] [-T] [-H] [-e]'''
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
		elif opt in ("-n", "--numbers"):
			convert_numbers_to_tokens = False
		elif opt in ("-d", "--dates"):
			convert_dates_to_tokens = False
		elif opt in ("-T", "--Times"):
			convert_times_to_tokens = False
		elif opt in ("-T", "--Hyperlinks"):
			convert_links_to_tokens = False
		elif opt in ("-e", "--escaped"):
			decode_escaped = False

	translate_table = dict((ord(char), None) for char in unicode(invalid_chars))
	sentences = Load_Files(inputfile)

	fo = open(outputfile, "w")
	for sentence in sentences:
		temp_sentence = sentence.decode('utf-8')
		temp_sentence = Normalize_Sentence(temp_sentence, convert_quotes_to_spaces)
		temp_sentence = Remove_Suffixes(temp_sentence, new_suffix_list)
		if convert_links_to_tokens == True:
			temp_sentence = Substitute_Links(temp_sentence)
		if decode_escaped == True:
			temp_sentence = Decode_Escaped(temp_sentence)
		if convert_dates_to_tokens == True:
			temp_sentence = Substitute_Dates(temp_sentence)
		if convert_times_to_tokens == True:
			temp_sentence = Substitute_Times(temp_sentence)
		if convert_numbers_to_tokens == True:
			temp_sentence = Substitute_Numbers(temp_sentence)
		tokenized_sentence = Naive_Tokenizer(temp_sentence)
		if Ignore_Long_Sentence(tokenized_sentence, max_tokens) == True:
			continue
		tokenized_sentence = Remove_Long_Tokens(tokenized_sentence, max_chars)
		if Ignore_Invalid_Sentence(tokenized_sentence, sentence_invalid_symbols, sentence_invalid_tokens) == True:
			continue
		tokenized_sentence = Remove_Invalid_Tokens(tokenized_sentence, token_invalid_symbols)
		final_sentence = " ".join(tokenized_sentence) + "\n"
		final_sentence = Clean_Sentence(final_sentence, translate_table)
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
	fo.write(sentence.encode('utf-8'))

def Decode_Escaped(sentence):
	"""
		Converts found escaped HTML and unicode symbols to
		their printable version
	""" 
	h = HTMLParser()
	sentence = h.unescape(sentence)

	return sentence

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
		Returns a tokenized sentence without tokens that include 
		invalidating_symbols
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
			return True
	dummy = Remove_Invalid_Tokens(tokenized_sentence, invalidating_symbols)	
	if len(dummy) < len(tokenized_sentence):
		return True

	return False

def Clean_Sentence(sentence, translate_table):
	"""
		Cleans sentence from invalid chars
	"""
	sentence = unicode(sentence)
	return sentence.translate(translate_table)

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

def Substitute_Links(sentence):
	"""
		Substitutes url addresses (http://, https://, ftp://) with special token.
	"""
	link_pattern = r"(\b(https?|ftp)://[^,\s]+)"
	sentence = re.sub(link_pattern, ' url_was_here ', sentence, flags=re.IGNORECASE) 
	return sentence

def Substitute_Times(sentence):
	"""
		Substitutes time expressions with special token. 
		Formats taken from http://php.net/manual/en/datetime.formats.time.php
	"""
	#frac = r"(.[0-9]+)"
	hh = r"(0?[1-9]|1[0-2])"
	HH = r"([01][0-9]|2[0-4])"
	meridian = r"([AaPp]\.?[Mm]\.?)"
	MM = r"([0-5][0-9])"
	tz = r"(\(?[A-Za-z]{1,6}\)?|[A-Z][a-z]+([_/][A-Z][a-z]+)+)"
	tzcorrection = r"((GMT)?[+-]" + hh + ":?" + MM + "?)"

	# Accepted time formats
	form1 = r"(\b" + hh + r"([.:]" + MM + r"){0,2}" + r" ?" + meridian + r"\b)"
	form2 = r"(\b" + HH + r"([.:]" + MM + r"){1,2}" + r" ?(" + tz + r"|" + tzcorrection + r")?\b)"
	form3 = r"(\b" + tzcorrection + r"\b)"

	time_pattern = form3 + r"|" + form2 + r"|" + form1 
	sentence = re.sub(time_pattern, ' time_was_here ', sentence) 
	return sentence

def Substitute_Dates(sentence):
	"""
		Substitutes all dates with special token. Formats taken from http://php.net/manual/en/datetime.formats.date.php
	"""
	daysuf = r"(st|nd|rd|th)"
	dd = r"([0-2]?[0-9]|3[01])" + daysuf + r"?"
	DD = r"(0[1-9]|[1-2][0-9]|3[01])"
	m = r"(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)"
	mm = r"(0?[0-9]|1[0-2])"
	y = r"(\d{1,4})"
	yy = r"(\d{2})"
	YY = r"(\d{4})"

	# Accepted date formats
	form1 = r"(\b" + mm + r"/" + dd + r"(/" + y + r")?\b)"
	form2 = r"(\b" + YY + r"/" + mm + r"/" + dd + r"\b)"
	form3 = r"(\b" + YY + r"-" + mm + r"(-" + dd + r")?\b)"
	form4 = r"(\b" + dd + r"[\.-]" + mm + "[\.-](" + YY + r"|" + yy + r")\b)"
	form5 = r"(\b" + dd + r"[ \.-]?" + m + r"([ \.-]?" + y + r")?\b)"
	#form9 = r"(\b" + dd + r"[ \.-]?" + m + r"\b)"
	form6 = r"(\b" + m + r"[ \.-]?" + YY + r"\b)"
	form7 = r"(\b" + YY + r"[ \.-]?" + m + r"\b)"
	form8 = r"(\b" + m + r"[ \.-]?" + dd + "[,\. " + daysuf + "]+(" + y + r")?\b)"
	form10 = r"(\b" + m + r"-" + DD + r"-" + y + r"\b)"
	form11 = r"(\b" + y + r"-" + m + r"-" + DD + r"\b)"

	date_pattern = form11 + r"|" + form10 + r"|" + form8 + r"|" + form7 + r"|" + form6 + r"|" + form5 + r"|" + form4 + r"|" + form3 + r"|" + form2 + r"|" + form1
	sentence = re.sub(date_pattern, ' date_was_here ', sentence, flags=re.IGNORECASE) 
	return sentence

def Substitute_Numbers(sentence):
	"""
		Substitutes all numbers with special token
	"""
	# two cases handle trailing/leading decimal mark
	sentence = re.sub(r"\b(\d+[.,';]?)+\b|\b[.,]\d+\b", ' number_was_here ', sentence) 
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