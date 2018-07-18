# Link Grammar API Interaction Libraries and CLI scripts

There are several command line scripts along with assotiated libraries for grammar test and evaluation located in
this directory. Command line scripts are usualy wrappers for library functions for handling command line arguments and
options.

## Libraries

`cliutils.py` - Set of functions for handling command line arguments, handy when writing CLI scripts.

`evaluate.py` - Set of functions for parse quality evaluation.

`lgparse.py` - Set of high level subroutines to parse corpus files using Link Grammar API or link-parser subprocess.

`optconst.py` - Set of bitmask constants, used for setting/resetting different parsing options when calling functions
from `lgparse.py` module.

`parse-stat.py` - Set of functions for parseability and parse quality estimation.

`psparse.py` - Set of functions for parsing postscript notated linkages, returned by Link Grammar API or link-parser


## Command Line Scripts

`grammar-test.py` - generated grammar test script (obsolete)

`grammar-test2.py`- second version of generated grammar test script capable of parsing multiple corpus files with
                    multiple dictionaries. Actually, it is a wrapper over set of high level Link Grammar parse
                    subroutines collected in `lgparse.py`.

`lgparser.py`     - parser script capable of parsing input corpus file using Link Grammar API and generating link output
                    in ULL defacto link output format.

`parse-eval.py` - parse quality estimation script


## Grammar Test Script In Depth Description

`grammar-test2.py` has multiple options and can be used to test grammar files over the specified corpus or simply
generate ULL output files. It is capable of taking folders with multiples files and subfolders as a single corpus
as well as taking a folder with multiple dictionary files to test each single grammar file separately over the same
input corpus.

### Options

```
    OPTIONS:
        -h  --help              Print usage info.
        -c  --caps              Leave CAPS untouched.
        -w  --right-wall        Keep RIGHT-WALL tokens.
        -r  --rm-dir            Remove grammar directory if it already exists.
        -n  --no-strip          Do not strip token suffixes.
        -u  --ull-input         ULL links are used as input. This option should be specified to use only sentences
                                    and filter out link lines.
        -l  --linkage-limit     Maximum number of linkages Link Grammar may return when parsing a sentence.
                                Default is one linkage.
        -g  --grammar-dir       Directory path where newly created grammar should be stored.
        -t  --template-dir      LG grammar directory to be used as template when creating new grammars directories.
                                If short name such as 'ru' is used, default route LG path for specified grammar is used.
        -f  --output-format     Parse output format, can be "ull" (default), "diagram", "postscript", "constituent"
        -e  --link-parser-exe   Use link-parser executable called in a separate process instead of API calls.
                                It could be handy when LG API crashes while parsing some specific dictionary rules or
                                test corpus sentences.
        -x  --no-left-wall      Exclude LEFT-WALL and period from statistics estimation.
        -s  --separate-stat     Generate separate statistics for each input file.
```



### Use Cases

#### ULL formated Output File Generation

In the example bellow the sctipt is executed using default language grammar (en). The output file will have the same
name as the input one.

`grammar-test2.py -i <my-input-file.txt> -o <my-output-directory> -f ull -e -u`

#### Grammar Test

`grammar-test2.py -d <dict-file> -i <input-file> -o <output-dir> -g <grammar-dir> -t <template-dir> -r -f ull -q -e -u`

`<dict-file>` - It can be either directory path, where dictionary files are located or path to a single properly notated
dictionary file, or a short name of any language, supported by Link Grammar such as `en`, `ru` etc.

`<input-file>` - Path to either input corpus file or input corpus directory.

`<output-dir>` - Path to output directory.

`<template-dir>` - Template grammar directory path. Because Link Grammar dictionary consists of at least four files,
template grammar directory path should be specified in order to let the script copy three more files from into a new
grammar dictionary folder along with dictionary file specified by `-d` option.
