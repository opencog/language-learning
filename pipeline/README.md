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
$ ull-cli -C Check-GCB-2018-12-14-500c-mwc\=1+.json --verbosity=warning --logging=debug
```

```
$ python tstr.py GT-CDS-LG-E-551-cDRKc-90119.json
$ python tstr.py GT-GCB-2018-12-14-500c-mwc=1.json
```
