# OpenCog Unsupervised Language Learning project

From now on it is assumed that you using Linux and have `anaconda3` or `miniconda3` installed on your machine. Othewise see 
https://conda.io/docs/user-guide/install/linux.html

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

## Download source code
```
git clone https://github.com/singnet/language-learning.git
```

## Create virtual environment
```
cd ~/language-learning
conda env create -f environment.yml
```

## Run tests
```
cd ~/language-learning
source activate ull
pytest
```
## Run Jupyter
```
cd ~/language-learning/notebooks
source activate ull
jupyter notebook
```

## Grammar Tester Installation

From `language-learning` directory run:

```
source activate ull
pip install .
```
If for some reason you are not using virtual environment or using Python 2.x along with Python 3.x make sure you 
run `pip3` instead:
```
pip3 install .
``` 

`opencog-ull` package will be installed to your virtual environment.
Command line scripts from `src/cli-scripts` are copied to `/bin` subdirectory in your virtual environment.

To uninstall the package type:
```
pip uninstall opencog-ull
```

## Running command line scripts

Command line scripts (which are located in `src/cli-scripts`) can be run from any location. In activated virtual 
environment type the name of the script you need to run. 

## Calling library functions from within your code

If you are going to use grammar tester from within your own code see `src/samples` for use cases.


---
