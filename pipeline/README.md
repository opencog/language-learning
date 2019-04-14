## "Mini-pipeline" `ppln.py`: CLI script to run Grammar Learner and Grammar Tester

## Environment

See **Anaconda virtual environment** section of the project [README](https://github.com/singnet/language-learning#anaconda-virtual-environment)

## Usage

```
$ cd ~/language-learning/pipeline
$ conda activate ull
(ull) $ python ppln.py config.json
```
Sample configuration files ⇒ .json files in the [pipeline](https://github.com/singnet/language-learning/tree/master/pipeline) directory.  
Grammar Learner parameters ⇒ Grammar Learner [README](https://github.com/singnet/language-learning/tree/master/src/grammar_learner#call-learner).    

Fast test with [CDS-LG-E-Clean-11-50.json](https://github.com/singnet/language-learning/blob/master/pipeline/CDS-LG-E-Clean-11-50.json) configuration:  
```
(ull) $ python ppln.py CDS-LG-E-Clean-11-50.json
``` 

## Grammar Tester CLI tests:

```
(ull) $ ull-cli -C Check-GCB-2018-12-14-500c-mwc\=1+.json --verbosity=warning --logging=debug
```

```
(ull) $ python tstr.py GT-CDS-LG-E-551-cDRKc-90119.json
(ull) $ python tstr.py GT-GCB-2018-12-14-500c-mwc=1.json
```

## Category tagger: alpha v.0.0.1 2019-01-29 
Replace words in .ull files with relevant categories from Link Grammar .dict.  

***ATTENTION! Just an experimental stub, issues found processing larger corpora :(***

### Usage:
```
    category_tagger -d <dict_path> -i <input_path> -o <output_path>  [OPTIONS]
    category_tagger -C <json-config-file>

    dict_path           Path to grammar file in Link Grammar .dict format.
    input_path          Input corpus file or directory path.
    output_path         Output directory path to store tagged .dict files.
    json-config-file    JSON configuration file path.

    OPTIONS:
        -h --help       Print usage info.
        -C <json-config-file>  All parameters set exclusively in the .json file
                        Other parameters and options ignored.
    """
```
Input files are read from the `input_path`, 
tagged copies are saved in the `output_path/tagged_ull` directory 
with the original names.

### Making script executable:
```
$ cd ~/language-learning/pipeline
$ chmod +x category_tagger 
$ export PATH=home/your_path/language-learning/pipeline:$PATH
```
Otherwise run script with `$ python category_tagger <...>` command

### Samples:
```
$ cd ~/language-learning/pipeline
$ conda activate ull
(ull) $ category_tagger
(ull) $ category_tagger -h
(ull) $ category_tagger -C CT-CDS-LG-E-551.json
(ull) $ category_tagger -d '/output/POC-English-2019-01-25/POC-English-Amb_LG-E-551_dDRKd_gen-rules/dict_4C_2019-01-25_0006.4.0.dict'  -i '/data/POC-English-Amb/LG-E-551' -o '/output/_cat_tagger_POC-E-551'
```
Running with empty parameters `$ category_tagger` performs fast self-test 
with parameters stored in the `pipeline/CT-CDS-LG-E-clean.json` configuration file.
  