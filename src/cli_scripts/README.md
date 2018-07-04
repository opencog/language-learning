# CLI scripts

This subdirectory contains command line scripts for handling different ULL pipeline operations. Command line scripts are usualy wrappers for library functions for handling command line arguments and
options.

## Command Line Scripts

`grammar-tester`-   second version of generated grammar test script capable of parsing multiple corpus files with
                    multiple dictionaries. Actually, it is a wrapper over set of high level Link Grammar parse
                    subroutines collected in `grammartest` package.

`parse-evaluator` - parse quality estimation script


## Grammar Test Script In Depth Description

`grammar-tester` has multiple options and can be used to test grammar files over the specified corpus or simply
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

`grammar-tester -i <my-input-file.txt> -o <my-output-directory> -f ull -e -u`

#### Grammar Test

`grammar-tester -d <dict-file> -i <input-file> -o <output-dir> -g <grammar-dir> -t <template-dir> -r -f ull -q -e -u`

`<dict-file>` - It can be either directory path, where dictionary files are located or path to a single properly notated
dictionary file, or a short name of any language, supported by Link Grammar such as `en`, `ru` etc.

`<input-file>` - Path to either input corpus file or input corpus directory.

`<output-dir>` - Path to output directory.

`<template-dir>` - Template grammar directory path. Because Link Grammar dictionary consists of at least four files,
template grammar directory path should be specified in order to let the script copy three more files from into a new
grammar dictionary folder along with dictionary file specified by `-d` option.

## Using `grammar-tester` With Configuration File

In some cases you may find more convenient to use grammar test script with 
JSON configuration file. One configuration file may contain several testing
configurations. General syntax is:
```
grammar-tester -C <config_file_path>
``` 
General JSON configuration file for any ULL component should have at least
two sections `component` and `parameters`.

For grammar test script general JSON config file looks like:
```
[
  {
    "component": "grammar-tester",
    "parameters": [
      {
        "input_grammar": "~/data/parses/AGI-2018-paper-data-2018-04-22/POC-English-NoAmb-LEFT-WALL+period",
        "input_corpus": "~/data/poc-english/poc_english_noamb.txt",
        "template_path": "~/data/dict/poc-turtle",
        "grammar_root": "~/data/dict",
        "output_path": "~/data2/parses/AGI-2018-paper-data-2018-04-22/POC-English-NoAmb-LEFT-WALL+period",
        "ref_path": "~/data/poc-english/poc_english_noamb_parse_ideal.txt",
        "parse_format": "ull",
        "linkage_limit": "100",
        "rm_grammar_dir": true,
        "use_link_parser": true,
        "ull_input": true,
        "ignore_left_wall": true,
        "ignore_period": true,
        "calc_parse_quality": true
      },
    ]
  }
 ]
```
There are two gems which are not available when running `grammar-tester`
in a standard way with multiple command line arguments. In JSON configuration
file you can specify multiple configurations in `parameters` section and you
can also specify using dashboard for summarizing parsing statistics in a 
single file. 

### Configuration Options Available For `grammar-tester`


|  Parameter  |  Type  |                    Meaning                 |  Values |
|-------------|--------|--------------------------------------------|---------|
|input_grammar| string | Path to `.dict` file to be tested          | Any valid path |
|input_corpus | string | Path to corpus file or directory           | Any valid path |
|template_path| string | Path to a valid Link Grammar dictionary to be used as a template when creating new dictionary with generated `.dict` file | Any valid path |
|grammar_root | string | Path to a directory new dictionary will be created in | Any valid path |
|output_path  | string | Path to store output parse and statistics files | Any valid path | 
|ref_path     | string | Path to a single reference file, or directory | Any valid path |
|parse_format | string | Type of parse output | ull, diagram, postscript, constituent_tree |
|linkage_limit| integer| Maximum number of linkages for Link Grammar to generate | 1-10000 | 
|rm_grammar_dir| boolean | Force grammar tester to remove existing grammar dictionary directory if it already exists. |true/false|
|use_link_parser|boolean | Force grammar tester to use `link-parser` executable in a separate process as a parser.| true/false|
|ull_input|boolean| Tells grammar tester that `.ull` file is used as an input corpus. When set to `true` lines starting with a digit are filtered out.| true/false|
|ignore_left_wall|boolean| If set to `true` `LEFT-WALL` and period links are ignored when parse statistics is estimated.|true/false|
|ignore_period|boolean| Force grammar tester to ignore period when parse statistics is estimated.| true/false|
|calc_parse_quality|boolean| If set to `true` parse quality is calculated.|true/false|
|keep_caps|boolean| Capitalized tokens are left untouched if set to `true`, lowered otherwise.| true/false|
|keep_rwall|boolean| Keep RIGHT-WALL if set to `true`|true/false|
|strip_suffix|boolean| Strip off token suffix if set to `true`.|true/false|
|dup_dict_path|boolean| Duplicate subdirectory structure of `input_grammar` directory if set to `true`.|true/false|
|separate_stat|boolean| Produce separate statistics file for each corpus file if set to `true`.|true/false|
|store_dict_localy|boolean| Create dictionary subdirectory in the same subdirectory where output files are stored.|true/false|
|no_left_wall_in_ull|boolean| Do not write `LEFT-WALL` links to `.ull` output file.|true/false|


## Configuring File Dashboard

File dashboard is defined by TextFileDashboard class and responsible for representation 
of parsing result statistics in a single table. 

In current version of the library dashboard is only available when using 
the script with `-C` option.

File dashboard configuration is defined in `.json` configuration file and 
only available when using `grammar-tester` script with `-C` option.   

Here is the list of configurable parameters:

`row_count` - Numeric value representing the number of rows, including 
headers, in the dashboard.  

`col_count` - Numeric value representing the number of columns in the 
dashboard.    

`row_key` - Format string used as a dictionary key when searching for 
row index number. Key format strings are explained later in this document.  

`col_key` - Format string, used as a dictionary key when searching for 
column index number. Key format strings are explained later in this document.

`value_keys` - List of format string parameters where each element defines
format string for corresponding data cell in the dashboard table.

`col_headers` - List of header string parameters. Because table header may
consist of multiple rows, each element of the list defines corresponding
header row. Each row is definded by one or many named parameters. 
In a simpliest case only `title` parameter may be specified. Header definition
is explained later in this document.

`row_indexes` - dictionary with row key values and lists of corresponding
row index numbers.  

`col_indexes` - dictionary with column key values and lists of corresponding
column indexes.

### How it works
Each dashboard class implements `on_statistics()` event handler which is 
invoked by the GrammarTester class instance every time the grammar file 
test against the given corpus is complete. There are several parameters 
supplied when calling the handler: list of graph nodes (dictionary path
subdirectories) given in reverse order i.e. `/home/alex/data/AGI-2018` is 
passed as `["AGI-2018", "data", "alex", "home"]`, parseability and parse 
quality data structures. The event handler makes up row and column key 
strings using `row_key` and `col_key` configuration parameters, finds
corresponding row and column indexes, makes up value string using `value_key`
format string and fills corresponding cell(s) of the table with the value
string.

### General Steps For File Dashboard Configuration
1. Define dashboard table structure.
2. Analyse graph (directory) structure and find out dashboard dimentions
and graph nodes responsible for row/column positioning inside the dashboard.
3. Define row/column key value format strings.
4. Define row/column key string/numeric row/column index relations.
5. Define headers structure.

### Key Format Parameters
`row_key`, `col_key` are Python format strings needed to make up strings 
used as dictionary keys to find corresponding row and column numbers.

`value_keys` is a list of format strings for each cell value in a table
row.

As in any Python format string `{0}` represents variable index. 

For `row_key` and `col_key` numeric value in curly braces represents graph 
(path) node index starting from zero. Because the number of nodes may 
vary, the nodes are passed in reverse order.
  
For `value_keys` format strings use named variables within curly braces.
Here is the list of available variables `nodes` (used with index), 
`parseability`, `parsequality`, `PQA`.

### Row And Column Search Definitions
There are two dictionaries created when `TextFileDashboard` class instance is initialized.
One of them defines a relation between graph (path) nodes and row index(s),
another one defines a relation between graph (path) nodes and column
index(s). Row and column indexes are represented by lists of numeric values
because one graph node value may influence multiple rows/columns in the
dashboard. Both dictionaries are initialized with corresponding `row_indexes`
and `col_indexes` configuration parameters. Key string in each of the above
mentioned parameters must correspond `row_key`/`col_key` format template.

### Column Headers
As soon as table header may have complex structure, parameter `col_headers` is 
represented by list of headers where each header is a list of columns. Each 
column is a dictionary. While each column header definition may consist of 
multiple named entries, only `title` is mandatory and should be assigned a 
text string. HTMLFileDashboard class instances may handle `col_span` and 
`row_span` attributes. 