#! /usr/bin/env python
# -*- coding: utf8 -*-

# ASuMa, Feb 2018
# Tokenizer that uses LG functionality

from linkgrammar import Linkage, Sentence, ParseOptions, Dictionary, Clinkgrammar as clg

any_dict = Dictionary() # Opens dictionary only once

en_lines = [
    'This is Mr. Wo_lf #test.',
    #'I feel is the exciter than other things', # from issue #303 (10 linkages)
]

po = ParseOptions(min_null_count=0, max_null_count=999)

for text in en_lines:
    sent = Sentence(text, any_dict, po)
    linkages = sent.parse()
    #linkage = Linkage(0, sent, po)
    for linkage in linkages:
	num_words = linkage.num_of_words()
    	for i in range(num_words - 1):
	    word_start = linkage.word_byte_start(i + 1)
	    word_end = linkage.word_byte_end(i + 1)
	    print(text[word_start:word_end])
	break
