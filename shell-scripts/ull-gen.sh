export PATH="/home/alex/PycharmProjects/language-learning/src/link_grammar:$PATH"

source activate ull

# Parse input file with default grammar 'en' and generate ULL formated output file
grammar-test2.py -i ~/data/poc-english/poc_english.txt -o ~/data/parses/AGI-2018/ -f ull -e -u
#grammar-test2.py -i ~/data/poc-english/poc_english_noamb.txt -o ~/data/parses/AGI-2018/ -f ull -e -u

source deactivate