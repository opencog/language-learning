# CLI scripts

This subdirectory contains command line scripts for handling different ULL pipeline operations. Command line scripts are usualy wrappers for library functions for handling command line arguments and
options.

## Command Line Scripts

|Name|Description|
|----|-----------|
|`dict-transformer`|Script, producing child dictionary file, containing subset for parent dictionary rules defined by one or more sentences|
|`grammar-tester` |Generated grammar test script capable of parsing multiple corpus files with multiple dictionaries. Actually, it is a wrapper over set of high level Link Grammar parse subroutines collected in `grammar_tester` package.|
|`parse-evaluator`|Parse quality estimation script|
|`sentence-counter`|Corpus sentence counter script|
|`token-counter`|Token apperance counter sctipt|
|`ull-cli`|Pipeline execution script|

## Grammar Test Script In Depth Description

`grammar-tester` has multiple options and can be used to test grammar files over the specified corpus or simply
generate ULL output files. It is capable of taking folders with multiples files and subfolders as a single corpus
as well as taking a folder with multiple dictionary files to test each single grammar file separately over the same
input corpus. Grammar evaluator is currently integrated into `grammar-tester` and can be used by specifying reference
ULL-file.

There are two ways to run `grammar-tester`. The first one is by specifying all parameters and options in the command 
line. The second one is by specifying JSON configuration file, where all necessary parameters and options are properly 
set. Each way has its own pros and cons. For example you do not have to write complex configuration file if you simply 
need to parse a single file using English grammar. On the other hand it is much more convenient to run `grammar-tester`
with properly prepared configuration file if you need to test several grammar files and get statistics total summary.

### Parameters And Options

```
Usage:

    grammar-tester -i <input_path> [-o <output_path> -d <dict_path>]  [OPTIONS]
    grammar-tester -C <json-config-file>

    dict_path           Path to grammar definition file (or directory with multiple such files) to be tested.
                        The files should be in proper Link Grammar .dict format. Language short name such as 'en' or
                        'ru' may also be specified. If no '-d' option is specified English dictionary ('en') is used
                        by default.
    input_path          Input corpus file or directory path. In case of directory the script will traverse all
                        subdirectories, parsing each file in there and calculating statistics for the whole corpus.
    output_path         Output directory path to store parse text files in. sys.stdout is used if not specified.
                        The program stores parses as text files one output file per one input file in
                        <output_path> directory keeping the same file name for the output file but adding extetions
                        depending on the specified output format.
                        The output file format depends on '-f' option specified. ULL format used if ommited.
                        If directory path is specified as <input_path>, the whole subdirectory tree is recreated
                        inside <output_path>/<dict_name>/ where each output file corresponds to the same input one.
    json-config-file    JSON configuration file path.

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
        -R  --reference         Path to reference file if single file specified by option '-i' as input corpus or path
                                to a directory with a number of reference files. In later case files with the same names
                                are being compared.
        -C  <json-config-file>  Force the script to use configuration data from JSON configuration file. If this option
                                is set, other options passed to the script are ignored.
        -D  <lang-short-name>   Language short name used by Link Grammar such as 'en' or 'ru'. One should avoid using
                                '-D' option along with '-d'. If both options are specified the latest one occurered in
                                the command line is used.
```

### Use Cases

#### ULL formated Output File Generation

In the example below the script is executed using default language grammar (en). If you need to use another language
you may specify it by option '-D' <lang>. The output file will have the same
name as the input one.

`grammar-tester -i <my-input-file.txt> -o <my-output-directory> -f ull -e -u`

#### Grammar Tester

`grammar-tester -d <dict-file> -i <input-file> -o <output-dir> -g <grammar-dir> -t <template-dir> -r -f ull -q -e -u`

`<dict-file>` - It can be either directory path, where dictionary files are located or path to a single properly notated
dictionary file, or a short name of any language, supported by Link Grammar such as `en`, `ru` etc.

`<input-file>` - Path to either input corpus file or input corpus directory.

`<output-dir>` - Path to output directory.

`<template-dir>` - Template grammar directory path. Because Link Grammar dictionary consists of at least four files,
template grammar directory path should be specified in order to let the script copy three more files from into a new
grammar dictionary folder along with dictionary file specified by `-d` option.

Use `grammar-tester` or `grammar-tester --help` for the list of options.

### `grammar-tester` tutorial

Make local copy of the following directory: http://langlearn.singularitynet.io/data/samples/grammar-tester/ .

`data` subdirectory contains sample data files.
`dict` subdirectory contains template grammar directory to be used for creating new LG dictionaries.
`*.dict` sample dictionary file(s).

### Few commands for most common tasks

As soon as `grammar-tester` can be used with both LG shipped/previously created dictionaries and dictionary files
generated by `grammar-learner` there two sets of frequently used commands.

## Commands to be used with LG-shipped English dictionary (can be any langeage)

```
grammar-tester -D en -c -x -i data/EnglishPOC.txt -o . -R data/EnglishPOC.txt.ull
```
and

```
grammar-tester -D en -c -u -x -i data/EnglishPOC.txt.ull -o . -R data/EnglishPOC.txt.ull
```
The two commands both use English dictionary for parsing input files specified by `-D en` option,
but differ in type of input corpus. The first one uses text file as an input. The second one uses `.ull` file as an 
input. In both cases LEFT-WALL and period are ignored by `-x` option. Letter cases are preserved by `-c` option. 

## Commands to be used for testing induced grammars

```
grammar-tester -d dict_37C_2019-04-19_0007.4.0.dict -r -L -c -x -i data/EnglishPOC.txt -o . -R data/EnglishPOC.txt.ull -t dict/poc-turtle
```
and
```
grammar-tester -d dict_37C_2019-04-19_0007.4.0.dict -r -L -c -u -x -i data/EnglishPOC.txt.ull -o . -R data/EnglishPOC.txt.ull -t dict/poc-turtle
```
The two command use the same induced dictionary file for testing, but as in previous example differ in type of input corpus.  
Option `-L` tells `grammar-tester` to create LG-style dictionaries in the output directory. Option `-u` is used when 
processing `.ull` input file.