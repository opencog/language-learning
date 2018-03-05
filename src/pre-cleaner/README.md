#ASuMa, Feb 2018

Directory for pre-cleaner tools: split-sentences.pl, pre-cleaner.py, and tokenizer.py

#########################################################################################
Sentence splitting is done by Multi-language sentence splitter from language learning pipeline: split-sentences.pl
**TODO***
- include arbitrary symbols to do sentence splitting. At least optionally colon and semi-colon.

**ISSUES**
- Doesn't split sentence if beginning is not capitalized (can add empty line or <P> line as a workaround)
- Sentences beginning with numbers don't get split (can add empty line or <P> line as a workaround)
- Escapes backslash, so pre-cleaner doesn't recognize unicode escape codes

#########################################################################################
Text-cleaning is done by pre-cleaner.py. It takes a file previously processed by sentences splitting. Main function documents all posibilities; they're copied here:
PreCleaner takes two mandatory arguments and several optional ones:

        PreCleaner takes two mandatory arguments and several optional ones:

        "Usage: pre-cleaner.py -i <inputfile> -o <outputfile> [-c <chars_invalid>] [-s <suffixes>] [-l <sentence_length>] [-t <token_length>] 
        [-x <sentence_symbols>] [-y <sentence_tokens>] [-z <token_symbols>] [-U] [-q] [-n] [-d] [-T] [-H] [-e]"

        inputfile           Name of inputfile
        outputfile          Name of ouputfile
        [
        chars_invalid       Characters to delete from text (default = none). They need to be given as a
                            string without spaces between the characters, e.g. "$%^&" would eliminate
                            only those 4 characters from appearances in the text.
        suffixes            Suffixes to eliminate in text (default = none). They need to come in a string
                            separated by spaces.
                            For example, -s "'s 'd n't" would eliminate all suffixes 's, 'd, n't
                            Of course, as suffixes, they need to come at the end of a word to be eliminated
        sentence_length     Maximum sentence length accepted (default = 16. Sentences with more are deleted)
        token_length        Maximum token lenght accepted (default = 25. Tokens with more are deleted)
        sentences_symbols   Symbols invalidating sentences (default = none). They need to be given as a
                            string without spaces between the characters, e.g. "$%^&" would eliminate
                            all sentences that have those 4 characters.
        sentence_tokens     Tokens invalidating sentences (default = none). They need to be given as a 
                            string separated by spaces, e.g. "three invalid tokens" would eliminate all
                            sentences including either "three", "invalid" or "tokens"
        token_symbols       Symbols invalidating tokens (default = none). They need to be given as a
                            string without spaces between the characters, e.g. "$%^&" would eliminate
                            all tokens that have those 4 characters.
        -U                  Flag to keep uppercase letters (default is to convert to lowercase)
        -q                  Flag to keep quotes (default is to convert them to spaces)
        -n                  Keep numbers (default converts them to @number@ token)
        -d                  Keep dates (default converts them to @date@ token)
        -T                  Keep times (default converts them to @time@ token)
        -H                  Keep hyperlinks (default converts them to @url@ token)
        -e                  Keep escaped HTML and UniCode symbols (default decodes them)
        ]
        
#########################################################################################
Tokenization is done by tokenizer.py, using LG 'any' language dictionary. 
tokenizer.py takes a file previously processed by sentences splitting, and optionally pre-cleaning. 
Main function documents arguments; they're copied here:

Tokenizer procedure that uses LG tokenizer with python bindings

        Usage: tokenizer.py -i <inputfile> -o <outputfile> [-S]

        inputfile           Name of inputfile
        outputfile          Name of ouputfile
        -S                  Don't remove sentence splitters added by 
                            pre-cleaner.py (default removes them)
