#ASuMa, Feb 2018. Updated, Apr 2018.

Directory for pre_cleaner tools.

###########################

The pre_cleaner pipeline can be run with script run_cleaner.sh, which will
call split-sentences.pl and pre_cleaner.py to process all files in the given
directory.
# Usage: FULL_PATH/run_cleaner <inputdir> <outputdir> 
#        [--nosplitter] [other args for pre_cleaner.py]
# --nosplitter option for some text formats where splitting the file is 
#              not necessary/convenient
# Run from inputdir's parent directory

If removing header is of interest, run cleaner_pipeline.sh 
instead of run_cleaner.sh
# Usage: cleaner_pipeline.sh <inputdir> <outputdir> [more args to run_cleaner]

The rest of the files in the folder are described below:

###############################

Sentence splitting is done by Multi-language sentence splitter from language
learning pipeline: split-sentences.pl
**TODO***
- include arbitrary symbols to do sentence splitting. At least optionally 
colon and semi-colon.

**ISSUES**
- If sentence doesn't end with end-of-sentence mark, it doesn't split (dot,
 question mark, etc), even if
  separate line

###############################
Text-cleaning is done by pre_cleaner.py. It takes a directory with files 
pre-processed with sentence splitter. Main function documents all 
posibilities; they're copied here:
        Pre_cleaner takes two mandatory arguments and several optional ones:

        ```
        "Usage: pre_cleaner.py -i <inputdir> -o <outputdir> [-c <chars_invalid>] [-b <bounday_chars>] 
        [-a <tokenized_chars>][-s <suffixes>] [-l <sentence_length>] [-t <token_length>] 
        [-x <sentence_symbols>] [-y <sentence_tokens>] [-z <token_symbols>] [-U] [-q] [-n] [-d] [-T] [-H] [-e]"

        inputdir            Directory with files to be processed.
                            Can contain subdirectories.
        outputdir           Directory to output processed files
        [
        chars_invalid       Characters to delete from text (default = none). They need to be given as a
                            string without spaces between the characters, e.g. "$%^&" would eliminate
                            only those 4 characters from appearances in the text.
        boundary_chars      Characters tokenized if token boundaries, only inside.
                            Default: apostrophe, double quote.
        tokenized_chars     Characters tokenized everywhere.
                            Default: brackets, parenthesis, braces, comma, colon, semicolon, slash,
                            currency signs, #, &, +, -
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
        -U                  Keep uppercase letters (default is to convert to lowercase)
        -q                  Pad quotes with spaces (default is to keep them as is)
        -j                  Separate contractions (default is to keep them together)
        -n                  Keep numbers (default converts them to @number@ token)
        -d                  Keep dates (default converts them to @date@ token)
        -T                  Keep times (default converts them to @time@ token)
        -H                  Keep hyperlinks/emails (default converts them to @url@/@email@ token)
        -e                  Keep escaped HTML and UniCode symbols (default decodes them)
        -S                  Don't add sentence splitter mark to be recognized by
                            split_sentences.pl, even if text is lowercased (they're added by default)
        ]
        ```        
##########################
Tokenization is done by tokenizer.py, using LG 'any' language dictionary. 
Main function documents arguments; they're copied here:

Tokenizer procedure that uses LG tokenizer with python bindings

        Usage: tokenizer.py -i <inputdir> -o <outdir>

        inputdir           Name of input directory
        outdir             Name of ouput directory
