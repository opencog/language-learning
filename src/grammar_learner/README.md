## Grammar Learner  
### `language-learner/src/grammar_learner/learner.py`
#### Call learner:
```
from src.grammar_learner.learner import learn_grammar
kwargs = {                              # defaults:
    'input_parses'  :   <input>     ,   # path to directory with input parses
    'output_grammar':   <output>    ,   # filename or path to store Link Grammar .dict file
    'output_categories' :    ''     ,   # category tree path = output_grammar if '' or not given
    'output_statistics' :    ''     ,   # input file stats = output_grammar if '' or not given
    'temp_dir'          :    ''     ,   # temporary files = language-learning/tmp/ if '' or not set
    'parse_mode'    :   'given'     ,   # 'given' (default) / 'explosive' (next)
    'left_wall'     :   ''          ,   # '','none' - don't use / 'LEFT-WALL' - replace ###LEFT-WALL###
    'period'        :   False        ,  # use period (full stop - end of sentence) in links learning: True/False
    'context'       :   2           ,   # 1: connectors / 2: disjuncts
    'window'        :   'mst'       ,   # 'mst' / reserved options for «explosive» parsing
    'weighting'     :   'ppmi'      ,   # 'ppmi' / future options
    'group'         :   True        ,   # group items after link parsing
    'distance'      :   False       ,   # reserved options for «explosive» parsing
    'word_space'    :   'discrete'  ,   # 'embeddings' / 'discrete' / sparse
    'dim_max'       :   100         ,   # max vector space dimensionality
    'sv_min'        :   0.1         ,   # minimal singular value (fraction of the max value)
    'dim_reduction' :   'none'      ,   # 'svm' / 'none' (discrete word_space, group)
    'clustering'    :   ('kmeans', 'kmeans++', 10), # 'kmeans' / 'group' -- see comments below
    'cluster_range' :   (50,2,5)    ,   # max, min, proof / or (20,200,5,3) -- see comments below
    'cluster_criteria': 'silhouette',   # optimal clustering criteria
    'cluster_level' :   1.0         ,   # level = 0, 1, 0.-0.99..: 0 - max number of clusters
    'categories_generalization': 'off', # 'off' / 'cosine' - cosine similarity, 'jaccard'
    'categories_merge'      :   0.8 ,   # merge categories with similarity > this 'merge' criteria
    'categories_aggregation':   0.2 ,   # aggregate categories with similarity > this criteria
    'grammar_rules' :   2           ,   # 1: 'connectors' / 2 - 'disjuncts'
    'rules_generalization'  :  'off',   # 'off' / 'jaccard' - group rules by jaccard similarity 
    'rules_merge'           :   0.8 ,   # merge rules with similarity > this 'merge' criteria
    'rules_aggregation'     :   0.2 ,   # aggregate rules similarity > this criteria
    'linkage_limit' : 1000          ,   # Link Grammar parameter for tests
    'tmpath' : module_path + '/tmp/',   # temporary files directory (legacy)
    'verbose': 'min'    # display intermediate results: 'none', 'min', 'mid', 'max'
}
response = learn_grammar(**kwargs)
```
### Comments to **kwargs:  
**Minimum parameters**: kwargs = {'input_parses': `<input path>`, 'output_grammar': `<output path>`}  
- `input_parses` <string> -- path to a directory with input parse files;  
- `output_grammar` <string> --  path to a file or directory, 
  in case of directory the grammar file is saved with auto file name `dict<...>.dict`;
- default stats and category tree files are saved to output_grammar directory  
  as `corpus_stats.txt` and `cat_tree.txt`.  

**clustering** -- tuple of values or string:  
- `('kmeans', 'kmeans++', 10)` -- default setting for kmeans algorithm: 
  kmeans++ initializations, 10 seed clustering attempts;
- `group` -- group identical lexical entries (ILE);  
- future options -- to be continued after Grammar learner 0.6 baselihne tests
  
**cluster_range** -- tuple of integers:
- `(max, min, proof)` -- find optimal number of clusters with maximum `cluster_criteria`
  within the range `min-max`,  
  `proof` -- number of best clustering variants with the same number of clusters 
  (various clusterings are possible in k-means clustering for a given number of clusters);  
- `(min, max, step, repeat)` -- search for a clustering with maximum `cluster_criteria`
  passing through the `min-max` range with `step`, taking the best clustering of `repeat` tests for each step.   
