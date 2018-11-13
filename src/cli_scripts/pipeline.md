# ULL Pipeline Execution
Pipeline is executed by `ull-cli` script responsible for parsing configuration file. It executes
each pipeline component specified in JSON configuration file. There are several pipeline components
available for now:
- text-parser - component responsible for tokenizing and parsing text files (only Link Grammar parser is
implemented in the current version of the library);
- grammar-learner - component which takes parses as input and produces grammar dictionaries in 
Link Grammar format;
- grammar-tester - takes previously induced grammar and produces parsing metrics while parsing input
corpus and comparing the outcome with well defined parses of the same corpus.
- dash-board - dash board component responsible for depicting tabular pipeline results.
- path-creator - pseudo component used to create directory structure.

The above list will be extended with further versions of the library.


## `ull-cli` Script
`ull-cli` parses each componet configuration and runs it either sequentialy or simultaneously in a 
separate process. You should supply properly compiled JSON configuration file when running the script.

```
ull-cli -C <config.json> [-p <number-of-processes>]

    config.json             - Pipeline configuration file.
    number-of-processes     - Integer value, specifying the number of processes the pipeline can derive.
```

## JSON Configuration File
Before making your own configuration file make sure you have studied sample configuration files in 
https://github.com/singnet/language-learning/tests/test-data/config/pipeline . For 
`POC-Turtle-GL-GT-DB.json` make sure you have changed line 37 to match the path of `language-learning`
directory on your computer.  


Each pipeline configuration file must consist of the list of available component configuration 
dictionaries. Each component dictionary section should have the following parameters:
- `component`
- `common-parameters` (may be ommited)
- `specific-parameters`

`component` is the string name of one of the available pipeline components. This parameter is 
mandatory.

`specific-parameters` is a list of dictionaries, where each dictionary specifies unique configuration
of the specified component. Pipeline script executes specified component as many times as the number 
of dictionaries in the list.
 
`common-parameters` is a dictionary of zero or many parameters common for all configurations of 
the specified component. It may be ommitted if unnecessary.

Each component code is executed as many times as the length of `specific-parameters` list. Each 
successive component followes the execution path of the previous one. If the previous component
has multiple execution paths specified by the `specific-parameters` section, each path is folloed
by the successive component unless explicitly specified by `follow_exec_path=false` parameter.

`type` is a string parameter that can be either "dynamic" or "static". Static components should be
declared in the very beginning of JSON configuration file. They are created once and live until the 
end of pipeline execution. Dynamic components are created and destroyed on the fly. If `type` is not
specified "dynamic" is used by default.


### Currently Available Components

|Component|Type|Description|
|---------|----|-----------|
|text-parser|dynamic| Text Parser component |
|grammar-learner|dynamic| Grammar Learner component|
|grammar-tester|dynamic| Grammar Tester component|
|dash-board|static| Dash-board component|
|path-creator|static| Path Creator component|

### Built-in Variables

|Variable| Description|
|--------|------------| 
|%ROOT| Pipeline root directory|
|%LEAF| Absolute target path based on %ROOT and 'specific-parameters'|
|%RLEAF| Target path relative to %ROOT based on 'specific-parameters'|
|%PREV[.var]| Reference to previous component scope variable. When `.var` is not specified `%PREV.LEAF` is used.|  
|%RPREV| Relative target path of the previous component scope.|

You can refer any previously defined parameter of the current scope simply by specifying '%' followed
by parameter name e.g. `%input_grammar`. To refer any variable of the previous scope one can specify 
'%PREV.' followed by parameter name e.g. `%PREV.input_grammar`.

### `pre_exec_req` and `post_exec_req`

In some cases you may need to do something before or after the component is executed. For example you 
may need to create some directory or put some value into a dashboard. In order for that you can specify 
pre component execution and/or post component execution events. 

Both `pre-exec-req` and `post-exec-req` are lists of dictionaries. Each dictionary defines a single
static component request. The only mandatory parameter of each dictonary is `obj` which specifies the 
name of the object instance and requested method separated by period e.g. 
`"post-exec-req": [{"obj": "stat.set", "row": "1", "col": "2", "val": "{F1}"}]`. 

