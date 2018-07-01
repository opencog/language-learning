# OpenCog Unsupervised Language Learning project

## Dependencies
* Anaconda 3
* Numpy
* Pandas
* Scikit-Learn
* Jupyter notebook
* Matplotlib
* Cython
* SparseSVD
* PyTest

## Create virtual environment
```
conda env create -f environment.yml
```
## Run tests
```
cd ~/language-learning
source activate ull3
pytest
```
## Run Jupyter
```
cd ~/language-learning/notebooks
source activate ull3
jupyter notebook
```

## Grammar Tester Installation

From `language-learning` directory run:

```
source activate ull3
pip install .
```
`opencog-ull` package will be installed to your virtual environment.
From `src/cli-scripts` copy `grammar-test.py` to your working directory.
To uninstall grammar tester type:
```
pip uninstall opencog-ull
```
If you are going to use grammar tester from within your own code you 
need to add the following import instruction to the top of your source 
file:
```
from ull.grammartest import test_grammar, test_grammar_cfg
```
If your planning to use GrammarTester class add:
```
from ull.grammartest import GrammarTester, GrammarTestError
```


---
