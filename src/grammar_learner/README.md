## Grammar Learner  
### `language-learner/src/grammar_learner/learner.py`
#### Call learner:
```
from src.grammar_learner.learner import learn_grammar
kwargs = {                              # defaults:
    # parsing:
    'input_parses'      : <input>   ,   # path to directory with input parses
    'output_grammar'    : <output>  ,   # filename or path to store Link Grammar .dict file
    'output_categories' :    ''     ,   # category tree path = output_grammar if '' or not given
    'output_statistics' :    ''     ,   # input file stats = output_grammar if '' or not given
    'temp_dir'          :    ''     ,   # temporary files = language-learning/tmp/ if '' or not set
    'parse_mode'    :   'given'     ,   # 'given' (default) / 'explosive' (next)
    'left_wall'     :   ''          ,   # '','none' - don't use / 'LEFT-WALL' - replace ###LEFT-WALL### tag with 'LEFT-WALL'
    'period'        :   False       ,   # use full stop - end of sentence in links learning
    # word (vector) space:
    'word_space'    :   'vectors'  ,    # 'embeddings' / 'discrete' / sparse
    'context'       :   2           ,   # 1: connectors / 2: disjuncts; 
    'window'        :   'mst'       ,   # 'mst' / reserved options for «explosive» parsing
    'group'         :   True        ,   # group items after link parsing / False reserved
    'distance'      :   False       ,   # / reserved options for «explosive» parsing
    'weighting'     :   'ppmi'      ,   # 'ppmi' in 'vectors' settings / future options
    # sparse word space cleanup:
    'min_word_count'        :   1   ,   # prune low-frequency words occurring less
    'min_word_frequency'    :   0.0 ,   # (reserved)
    'max_words'             : 100000,   # (reserved) max number of words in vector space
    'min_link_count'        :   1   ,   # prune low-frequency connectors or disjuncts (see 'context')
    'min_link_frequency'    :   0.0 ,   # (reserved)
    'max_features'          : 100000,   # (reserved) max number of disjuncts or connectors
    'min_co-occurrence_count'   :  1,   # prune word-link co-occurrence matrix  
    'min_co-occurrence_frequency': 0.0, # (reserved)
    # 'embeddings' 'word_space': 
    'dim_reduction' :   'svd'       ,   # 'svd' / 'none' for 'discrete', 'sparse' word_space
    'dim_max'       :   100         ,   # max vector space dimensionality for SVD
    'sv_min'        :   0.1         ,   # minimal singular value (fraction of the max value)
    # clustering:
    'clustering'    :   'kmeans'    ,   # 'kmeans' / 'group' / 'agglomerative'... -- see comments below
    'cluster_range' :   [2,50,1,1]  ,   # min, max, step, repeat / other options described below
    'cluster_criteria'  : 'silhouette', # optimal clustering criteria (legacy for 'kmeans' 'clustering')
    'clustering_metric' : ['silhouette', 'cosine'], # new setting (October 2018) -- comments below
    'cluster_level' :   1.0         ,   # level = 0, 1, 0.-0.99..: 0 - max number of clusters
    # word categories generalization:
    'categories_generalization': 'off', # 'off' / 'jaccard'
    'categories_merge'      :   0.8 ,   # merge categories with similarity > this 'merge' criteria
    'categories_aggregation':   0.2 ,   # aggregate categories with similarity > this criteria
    # grammar induction and generalization:
    'grammar_rules' :   2           ,   # 1: 'connectors' / 2 - 'disjuncts'
    'rules_generalization'  :  'off',   # 'off' / 'jaccard' - group ILE-based rules by jaccard similarity 
    'rules_merge'           :   0.8 ,   # merge rules with similarity > this 'merge' criteria
    'rules_aggregation'     :   0.2 ,   # aggregate rules similarity > this criteria
    # miscellaneous:
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

**'clustering'** -- string or list:  
- `'kmeans'` or `['kmeans', 'kmeans++', 10]` -- default settings for k-means clustering 
  in `word_space` == 'embeddings' setting: `'kmeans++'` initializations, `10` seed clustering attempts;
- `'group'` -- group identical lexical entries (ILE) in `discrete` `word_space` setting;
- `'agglomerative'` or `['agglomerative', 'ward']` -- default settings for agglomerative clustering.  
More options: `['agglomerative', linkage, affinity]`:  
  - `linkage` -- linkage criterion: 'ward', 'complete', 'average', 'single';  
  - `affinity` -- metric used to compute the linkage: 'euclidean', 'l1', 'l2', 'manhattan', 'cosine'; 
  only 'euclidean' for 'ward' `linkage`;  
  - future options: `connectivity`, `compute_full_tree`, 'precomputed' affility callable/
  - more information ⇒ [sklearn.cluster.AgglomerativeClustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html)
- `mean shift` -- mean shift clustering, coming soon...
 
**'cluster_range'** -- list of integers:
- `[max, min, proof]` -- find optimal number of clusters with maximum `cluster_criteria`
    within the range `min-max`,  
    `proof` -- number of best clustering variants with the same number of clusters  
    (various clusterings are possible in k-means clustering for a given number of clusters);  
- `[min, max, step, repeat]` -- search for a clustering with maximum `cluster_criteria`
    passing through the `min-max` range with `step`, 
    taking the best clustering of `repeat` tests for each step;  
- `[n_clusters, n_tests)` -- return the best clustering of `n_tests` attempts for `n_clusters` by max `cluster_criteria`.  

**'clustering_metric'** -- tuple of strings:    
`(quality_metric, similarity_metric)`: -- clustering quality metric and vector similarity metric:  
- quality metric options: `silhouette`, `variance_ratio` / other options coming;  
- similarity metrics  for `silhouette` index: `cosine`, `jaccard`, `euclidean`, `chebyshev`. 

**'cluster_level'** -- float 0.0 - 1.0 (k-means, agglomerative clustering): 
optimal number of clusters: minimal, providing `clustering_metric` better than share of maximum value:
- 1.0 -- clustering, providing max value of `clustering_metric`;  
- x = 0.1-0.99 -- clustering with minimal number of clusters, providing x * max value of `clustering_metric`;
- 0 / 0.0  -- return clustering with maxi,al possible number of clusters