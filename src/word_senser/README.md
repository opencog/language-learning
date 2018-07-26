Files in this folder allow disambiguation of words in a corpus, given
unlabelled text as input, as well as evaluation tools.

*********************************************************************

- `train_multiple_adagram.sh` allows to automatically train a number of models
  with different parameters for the same corpus and dictionary. 
  The parameters to explore and Adagram's path are specified inside the file.
  Corpus should be pre-processed, 
  for example with language-learning/src/pre_cleaner tools, including tokenizer.py.
  For details about AdaGram's parameters and dictionary file, please refer to
  AdaGram's documentation.

```
Usage: ./train_multiple_adagram.sh <corpus> <dictionary>

```

*********************************************************************

- Given a folder with trained AdaGram models and a one with corpus files, 
  `annotate_corpus.sh` will return a folder with the annotated corpus where 
  those words that are ambiguous are tagged with their sense.
```
usage: annotate_corpora.sh [--window WINDOW] [--min-prob MIN-PROB] 
						  [--joiner SYMBOL] [-h] 
                		  model corpus output
```
Here is the description of all parameters:
* `WINDOW` is half the max size of the context for finding
  the sense of a word, by querying the AdaGram model with it.
* `MIN-PROB` specifies the minimum probability of a sense in the trained
  AdaGram model to be included in the annotated corpus. If a word in the model
  has only one sense above MIN-PROB, then the word is considered unambiguous.
* `SYMBOL` is the symbol to annotate words in the corpus. Default is "@".
  E.g. saw@tool
* `model` — path to directory with AdaGram models to use for disambiguation.
* `corpus` — path to folder with corpus to annotate. Corpus files are expected 
  to contain only one sentence per line and be fully tokenized.
* `output` — path to folder for saving the annotated corpus.

******************************************************************************

- Given a trained AdaGram model, `output_AdaGram_text.sh` returns all word
  senses included in the model above the optional threshold. File format
  is as specified in 
  https://docs.google.com/document/d/14MpKLH5_5eVI39PRZuWLZHa1aUS73pJZNZzgigCWwWg/edit#bookmark=id.7lkbw4yemsw2
```
usage: output_senses.sh [--neighbors NEIGHBORS] [--min-prob MIN-PROB] 
						[-h]
                		model output
```
Here is the description of all parameters:
* `NEIGHBORS` is the number of nearest neighbors to output for each word sense
* `MIN-PROB` specifies the minimum probability of a sense in the trained
  AdaGram model to be included in the output.
* `model` — path to AdaGram model to print out.
* `output` — path to output the model's senses.
 
***********************************************

`evaluate_WSD.py` returns ARI, F-SCORE, and V-SCORE for a sense-annotated corpus,
using a gold-standard annotated corpus as a reference.