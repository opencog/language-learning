# Link Grammar API Interaction Libraries and CLI scripts

There are several command line scripts along with assotiated libraries for grammar test and evaluation located in
this directory. Command line scripts are usualy wrappers for library functions for handling command line arguments and
options.

## Libraries

`cliutils.py` - set of functions for handling command line arguments

`evaluate.py` - set of function for parse quality evaluation

`lgparse.py` - set of high level subroutines to parse corpus files using Link Grammar API or link-parser subprocess.

`optconst.py` - set of bitmask constants, used for setting/resetting different parsing options when using functions from
`lgparse.py` module.

`parse-stat.py` - set of functions for parseability and parse quality estimation

`psparse.py` - set of functions for parsing postscript notated linkages, returned by Link Grammar API or link-parser


## Command Line Scripts

`grammar-test.py` - generated grammar test script (obsolete)

`grammar-test2.py`- second version of generated grammar test script capable of parsing multiple corpus files with
                    multiple dictionaries. Actually, it is a wrapper over set of high level Link Grammar parse
                    subroutines collected in `lgparse.py`.

'lgparser.py'     - parser script capable of parsing input corpus file using Link Grammar API and generating link output
                    in ULL defacto link output format.

`parse-eval.py` - parse quality estimation script