# SingularityNET Unsupervised Language Learning project

## Dependencies
* Anaconda 3 Python 3.6
* numpy, pandas, scipy, scikit-learn, cython
* SparseSVD Anaconda package
* Jupyter notebook
* Matplotlib

## Download source code  
Fork https://github.com/singnet/language-learning.git to your_repo  
```
$ git clone https://github.com/your_repo/language-learning.git
```

## Anaconda virtual environment

We use Ubuntu 16.04 LTS and `miniconda3`version of Anaconda. Please check [Anaconda guides](https://conda.io/docs/user-guide/install/linux.html)

### Create virtual environment
```
$ cd ~/language-learning
$ conda env create -f conda-env-ull.yml
```

`ull` environment includes necessary packages, matplotlib and Jupyter notebook.  
You can add packages and update environment at your own risk.  

### Other environments:
* `conda-env-ull-cli.yml` -- simplified for CLI: no Jupyter notebook, matplotlib.  
* `conda-env-ull-dev.yml` -- development environment with extended package set.

### Update environment:
Update with new environment file from [Github repository](https://github.com/singnet/language-learning) recommended:
```
$ cd ~/language-learning
$ git pull
$ conda env update -n ull -f conda-env-ull.yml --prune
```
The `--prune` key would force remove packages not specified in the `.yml` file.
If you have added come packages to the environment, you would rather let them prune and add after the update. Otherwise vwrsion conflicts might occur.  
You might need to reinstall Grammar Tester after environment update.

## Grammar Tester 

### Installation

From `language-learning` directory run:

```
$ source activate ull
$ pip install .
```
If for some reason you are not using virtual environment or using Python 2.x along with Python 3.x make sure you
run `pip3` instead:
```
$ pip3 install .
```

`opencog-ull` package will be installed to your virtual environment.
Command line scripts from `src/cli-scripts` are copied to `/bin` subdirectory in your virtual environment.

To uninstall the package type:
```
$ pip uninstall opencog-ull
```

### Running command line scripts

Command line scripts (which are located in `src/cli-scripts`) can be run from any location. In activated virtual
environment type the name of the script you need to run.

### Calling library functions from within your code

If you are going to use grammar tester from within your own code see `src/samples` for use cases.


## Jupyter notebooks

### Running on a local machine (with opencog-ull istalled)
```
$ cd ~/language-learning
$ source activate ull
$ jupyter notebook
```
Check sample notebooks in /notebooks directory.

## Runing Jupyter notebooks on a server  

Terminal:  
```
$ ssh -L 8000:localhost:8888 login@server.ip.address  
$ screen  
sh-4.3$ cd language-learning  
sh-4.3$ source activate ull  
(ull) sh-4.3$ jupyter notebook --no-browser --port=8888
#...
[...NotebookApp] The Jupyter Notebook is running at:
[...NotebookApp] http://localhost:8888/?token=(copy_this_token)  
```
Browser: `http://localhost:8000/?token=(token_copied_in_the_terminal)`  

## Running "mini-pipeline": Grammar Learner & Tester
```
$ cd ~/language-learning/pipeline
$ python ppln.py config.json
```
Details ⇒ [ppln README](https://github.com/singnet/language-learning/tree/master/pipeline)

---
