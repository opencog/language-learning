#ASuMa, Feb 2018

Directory for pre-cleaner tools

TODO: Implement tokenizer that works the same as Link-Grammar "any" language tokenizer

Sentence splitting is done by Multi-language sentence splitter from language learning pipeline: split-sentences.pl
TODO: include arbitrary symbols to do tokenization. At least optionally colon and semi-colon.

Text-cleaning is done by pre-cleaner.py. It takes a file previously processed by sentences splitting. Main function documents all posibilities. Those are copied here:
PreCleaner takes two mandatory arguments and several optional ones:

        inputfile           Name of inputfile
        outputfile          Name of ouputfile
        [
        chars_invalid       characters to delete from text
        suffixes            Suffixes to eliminate in text, need to come in a string, separated by spaces.
                            For example, -s "'s 'd n't" would eliminate all suffixes 's, 'd, n't
                            Of course, as suffixes, they need to come at the end of a word to be eliminated
        sentence_length     maximum sentence length accepted (sentences with more are deleted)
        token_length        maximum token lenght accepted (tokens with more are deleted)
        sentences_symbols   symbols invalidating sentences
        sentence_tokens     tokens invalidating sentences
        token_symbols       symbols invalidating tokens
        -U                  flag to keep uppercase letters (default is to convert to lowercase)
        -q                  flag to keep quotes (default is to convert them to spaces)
        ]

