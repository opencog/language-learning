# `grammartest` package 

This subdirectory contains several library files which make up `grammartest` package. 
As the name suggests, the purpose of the package is to test and evaluate induced grammar.


## Configuring File Dashboard

File dashboard is defined by TextFileDashboard class and responsible for representation 
of parsing result statistics in a single table. 

In current version of the library dashboard is only available when using 
the script with `-C` option.

File dashboard configuration is defined in `.json` configuration file and 
only available when using `grammar-test.py` script with `-C` option.   

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
`parseability`, `parsequality`.

### Row And Column Search Definitions
There are two dictionaries created when `TextFileDashboard` is initialized.
One of them defines a relation between graph (path) nodes and row index(s),
another one defines a relation between graph (path) nodes and column
index(s). Row and column indexes are represented by lists of numeric values
because one graph node value may influence multiple rows/columns in the
dashboard. Both dictionaries are initialized with corresponding `row_indexes`
and `col_indexes` configuration parameters. Key string in each of the above
mentioned parameters must correspond `row_key`/`col_key` format template.
   