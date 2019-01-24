## "Mini-pipeline" `ppln.py`: CLI script to run Grammar Learner and Grammar Tester

## Environment

See **Anaconda virtual environment** section of the project [README](https://github.com/singnet/language-learning)

## Usage

```
$ cd ~/language-learning/pipeline
$ python ppln.py config.json
```
Sample configuration files ⇒ .json files in the language-learning/pipeline directory.  
Grammar Learner parameters ⇒ Grammar Learner [README](https://github.com/singnet/language-learning/tree/master/src/grammar_learner) 

## Grammar Tester CLI tests:

```
$ ull-cli -C Check-GCB-2018-12-14-500c-mwc\=1+.json --verbosity=warning --logging=debug
```

```
$ python tstr.py GT-CDS-LG-E-551-cDRKc-90119.json
$ python tstr.py GT-GCB-2018-12-14-500c-mwc=1.json
```
