## Run Jupyter notebook
```
$ cd ~/language-learning
$ source activate ull
$ jupyter notebook
```
If a new tab or window would not open in your browser, 
copy the URL `http://localhost:8888/?token...` in the terminal 
and paste it in a new browser tab.  

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

## Archive:  

 2018: [static html copies of notebooks](http://langlearn.singularitynet.io/data/clustering_2018/html/), 
 [data](http://langlearn.singularitynet.io/data/clustering_2018/)    
 2019: [static html copies of notebooks](http://langlearn.singularitynet.io/data/clustering_2019/html/), 
 [data](http://langlearn.singularitynet.io/data/clustering_2019/) 
         
---

