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
https://github.com/singnet/language-learning/tests/test-data/config .


Each pipeline configuration file must consist of the list of available component configuration 
dictionaries. Each component dictionary section should have the following parameters:
- component
- common-parameters (may be ommited)
- specific-parameters

`component` is the string name of one of the available pipeline components. This parameter is 
mandatory.

`specific-parameters` is a list of dictionaries, where each dictionary specifies unique configuration
of the specified component. Pipeline script executes specified component as many times as the number 
of dictionaries in the list.
 
`common-parameters` is a dictionary of zero or many parameters common for all configurations of 
the specified component. It may be ommitted if unnecessary.
