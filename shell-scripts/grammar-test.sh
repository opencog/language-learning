export PATH="/home/alex/PycharmProjects/language-learning/src/link_grammar:$PATH"

source activate ull

OTYPE="diagram"

WALL="-i"

ROOT="~/data/parses/AGI-2018-paper-data-2018-04-22"
EREF="~/data/poc-english/poc_english_noamb_parse_ideal.txt"
TREF="~/data/parses/poc-turtle/poc-turtle-parses-expected.txt"
ENG1="POC-English-NoAmb-LEFT-WALL+period"
ENG2="POC-English-Noamb-no-LEFT-WALL"
TUR1="POC-Turtle-LEFT-WALL+period"
TUR2="POC-Turtle-no-LEFT-WALL"


# Parse POC-Turtle-LEFT-WALL+period three times for three different output formats
grammar-test2.py -d $ROOT/$TUR1 -i $TREF -o $ROOT/$TUR1 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f diagram -q -e -u
grammar-test2.py -d $ROOT/$TUR1 -i $TREF -o $ROOT/$TUR1 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f postscript -q -e -u
grammar-test2.py -d $ROOT/$TUR1 -i $TREF -o $ROOT/$TUR1 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f ull -q -e -u

# Evaluate POC-Turtle-LEFT-WALL+period parses
parse-eval.py -r $TREF -t $ROOT/$TUR1 $WALL

# Parse POC-Turtle-no-LEFT-WALL three times for three different output formats
grammar-test2.py -d $ROOT/$TUR2 -i $TREF -o $ROOT/$TUR2 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f diagram -q -e -u -x
grammar-test2.py -d $ROOT/$TUR2 -i $TREF -o $ROOT/$TUR2 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f postscript -q -e -u -x
grammar-test2.py -d $ROOT/$TUR2 -i $TREF -o $ROOT/$TUR2 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f ull -q -e -u -x

# Evaluate POC-Turtle-no-LEFT-WALL parses
parse-eval.py -r $TREF -t $ROOT/$TUR2 $WALL

# Parse POC-English-NoAmb-LEFT-WALL+period three times for three different output formats
grammar-test2.py -d $ROOT/$ENG1 -i $EREF -o $ROOT/$ENG1 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f diagram -q -e -u
grammar-test2.py -d $ROOT/$ENG1 -i $EREF -o $ROOT/$ENG1 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f postscript -q -e -u
grammar-test2.py -d $ROOT/$ENG1 -i $EREF -o $ROOT/$ENG1 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f ull -q -e -u

# Evaluate POC-English-NoAmb-LEFT-WALL+period parses
parse-eval.py -r $EREF -t $ROOT/$ENG1 $WALL

# Parse POC-English-Noamb-no-LEFT-WALL three times for three different output formats
grammar-test2.py -d $ROOT/$ENG2 -i $EREF -o $ROOT/$ENG2 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f diagram -q -e -u -x
grammar-test2.py -d $ROOT/$ENG2 -i $EREF -o $ROOT/$ENG2 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f postscript -q -e -u -x
grammar-test2.py -d $ROOT/$ENG2 -i $EREF -o $ROOT/$ENG2 -g ~/data/dict -t ~/data/dict/poc-turtle -r -f ull -q -e -u -x

# Evaluate POC-English-Noamb-no-LEFT-WALL parses
parse-eval.py -r $EREF -t $ROOT/$ENG2 $WALL

source deactivate