# language-learning/src/grammar_learner/generalization.py               80925
from copy import copy, deepcopy
from operator import itemgetter
from .clustering import cluster_id


def aggregate(categories, threshold, similarity_function, verbose='none'):
    cats = deepcopy(categories)
    if verbose == 'debug':
        print('aggregate: len(cats)[cluster]:', len(cats['cluster']), 'cats[cluster][-1]:', cats['cluster'][-1])
        print('aggregate: len(cats)[children]:', len(cats['children']))
        print('aggregate: cats lengths:', set([len(x) for x in cats.values()]))
    similar_clusters = []
    similarities = []
    ncats = len(cats['words'])

    for i,x in enumerate(cats['djs']):
        if i == 0: continue
        if cats['parent'][i] > 0: continue
        for j in range(i+1, ncats):  #TODO: max(i+1, counted_clusters) # don't repeat similarity
            if cats['parent'][j] > 0: continue
            similarity = similarity_function(x, cats['djs'][j])
            if similarity > threshold:
                similar_clusters.append([i,j, similarity])
            #-if similarity > aggregate and similarity < merge:
            similarities.append(round(similarity,2))

    if verbose == 'debug':
        print('aggregate: merge similar_clusters:', similar_clusters)
    merges = [{x[0],x[1]} for x in similar_clusters if x[2] > threshold]
    merged = []
    for m,mset in enumerate(merges):
        if m in merged: continue
        for k in range(m+1, len(merges)):
            if k in merged: continue
            #-print('m,k:', m,k)
            if len(mset & merges[k]) > 0:
                if verbose == 'debug':
                    print()
                if mset|merges[k] not in merges:
                    merges.append(mset|merges[k])
                merged.extend([m,k])
                if verbose == 'debug':
                    print('aggregate:', mset, merges[k], '⇒', mset|merges[k],
                          '\n- merged:', merged, '\n- merges:', merges)
    merges = [x for i,x in enumerate(merges) if i not in merged]
    if verbose == 'debug':
        print('aggregate: new merges:', merges)
        print('aggregate: cats lengths:', \
              ', '.join([k+':'+str(len(v)) for k,v in cats.items()]))
    for mset in merges:
        new_cluster_id = len(cats['parent'])
        if verbose == 'debug':
            print('aggregate: new_cluster_id:', new_cluster_id, ncats)
            print('aggregate: cats lengths before append:', \
                  ', '.join([k+':'+str(len(v)) for k,v in cats.items()]))

        #-cats['cluster'].append('C'+str(new_cluster_id))   # 80925 C01 ⇒ AB:
        cats['cluster'].append(cluster_id(new_cluster_id, new_cluster_id))
        # TODO: check situation new_cluster_id > 26**n      # 80925

        cats['parent'].append(0)
        cats['children'].append(mset)
        cats['words'].append(set())
        cats['disjuncts'].append(set())
        cats['djs'].append(set())
        cats['counts'].append(0)
        cats['quality'].append(threshold)
        if verbose == 'debug':
            print('aggregate: cats lengths after append:', \
                  ', '.join([k+':'+str(len(v)) for k,v in cats.items()]))
        for cluster in mset:
            cats['parent'][cluster] = new_cluster_id
            cats['words'][new_cluster_id].update(cats['words'][cluster])
            cats['disjuncts'][new_cluster_id].update(cats['disjuncts'][cluster])
            cats['djs'][new_cluster_id].update(cats['djs'][cluster])
            cats['counts'][new_cluster_id] += cats['counts'][cluster]
            #?cats['similarities'][new_cluster_id]
        cats['similarities'].append([0 for word in cats['words'][new_cluster_id]])

        if verbose == 'debug':
            print('aggregate: words['+str(new_cluster_id)+']:', \
                  cats['words'][new_cluster_id])
            print('aggregate: djs['+str(new_cluster_id)+']:', \
                  cats['djs'][new_cluster_id])
            print('aggregate: similarities['+str(new_cluster_id)+']:', \
                  cats['similarities'][new_cluster_id])
            if len(set([len(x) for x in cats.values()])) > 1:
                print('aggregate: cats lengths:', \
                      ', '.join([k+':'+str(len(v)) for k,v in cats.items()]))
            else: print('aggregate: cats lengths:', \
                        set([len(x) for x in cats.values()]))

    return cats, sorted(set(similarities), reverse=True)


def reorder(cats):
    # Parents: top clusters
    top_clusters = [(i,len(cats['words'][i])) for i,x in enumerate(cats['parent']) \
                    if x == 0 and i > 0]
    top = [0] + [x[0] for x in sorted(top_clusters, key=itemgetter(1), reverse=True)]
    ordnung = copy(top)
    #_ordnung = copy.deepcopy(top)  #if the list contains objects and you want to copy them as well

    # Children branches
    def branch(i, children):
        if children[i] == 0:
            return []
        else:
            x = []
            #TODO? define order of chidren?
            for j in children[i]:
                x.append(j)
                y = branch(j, children)
                if len(y) > 0: x.extend(y)
            return x
    for j,k in enumerate(top):      #_top, not ordnung - only top level clusters
        branchi = branch(k, cats['children'])
        if len(branchi) > 0:
            ordnung.extend(branchi)

    new_cats = {}
    new_cats['parent'] = [ordnung.index(cats['parent'][i]) for i in ordnung]

    n = sum(1 for i in new_cats['parent'] if i == 0)
    new_cats['cluster'] = [cluster_id(i, n) if x == 0 else None
        for i, x in enumerate(new_cats['parent'])]

    for key in cats.keys():
        if key not in ['cluster', 'parent']:
            new_cats[key] = [cats[key][i] for i in ordnung]

    for i,item in enumerate(new_cats['children']):
        if type(item) is set and len(item) > 0:
            new_cats['children'][i] = set([ordnung.index(x) for x in item])

    rules = [i for i,x in enumerate(new_cats['parent']) \
             if (x == 0 and i > 0)] # and type(list(new_cats['parent'][i])[0]) is tuple)]
    sign = lambda x: (1, -1)[x < 0]
    for rule in rules:
        if type(list(new_cats['disjuncts'][rule])[0]) is tuple:
            new_rule = []
            for disjunct in new_cats['disjuncts'][rule]:
                new_dj = []
                for index in disjunct:
                        new_dj.append(ordnung.index(abs(index)) * sign(index))
                new_rule.append(tuple(new_dj))
            new_cats['disjuncts'][rule] = set(new_rule)

    return new_cats


def jaccard(x,y):
    try:
        xx = set(x)
        yy = set(y)
    except: return 0
    if len(xx) == 0 or len(yy) == 0:
        return 0
    elif len(xx.union(yy)):
        return len(xx.intersection(yy))/len(xx.union(y))
    else: return 0


def generalize_categories(categories, **kwargs):   #80616 v.0.5
    # cats - {'cluster':[], 'words': [], 'disjuncts':[], ...]) from ile_df2cats_dict(clusters)
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    grammar_rules   = kwa(1, 'grammar_rules')
    aggregation     = kwa('off','categories_generalization')
    merge_threshold = kwa(0.8,  'categories_merge')
    aggr_threshold  = kwa(0.2,  'categories_aggregation')
    verbose         = kwa('none', 'verbose')

    if verbose in ['debug', 'max']:
        print('generalize_categories: based on Jaccard index')
        if len(set([len(x) for x in categories.values()])) > 1:
            print('cats lengths:', \
                ', '.join([k+':'+str(len(v)) for k,v in categories.items()]))
        else: print('cats lengths:', set([len(x) for x in categories.values()]))

    threshold = merge_threshold
    cats, similarities = aggregate(categories, threshold, jaccard, verbose)
    #TODO: list of merged clusters - to delete
    #TODO: delete merged clusters

    z = len(similarities)
    sims = similarities
    while z > 1 and threshold > aggr_threshold:
        if verbose == 'debug': print('threshold:', threshold)
        cats, similarities = aggregate(cats, threshold, jaccard, verbose)
        sims = [x for x in similarities if x < threshold]
        if verbose == 'debug': print('similarities:', similarities, '\n- sims:', sims)
        threshold = max(sims) - 0.01  # 0.001 ?
        z = len(sims)

    return reorder(cats), {'similarity_thresholds': sims}


#TODO: update and use or delete?
def aggregate_word_categories(clusters, **kwargs):  # 80523 +updates ~80616
    # clusters - pd.DataFrame(['cluster', 'cluster_words', 'disjuncts'])
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    aggregation     = kwa('off',    'categories_generalization')
    merge           = kwa(0.8,      'categories_merge')
    aggregate       = kwa(0.2,      'categories_aggregation')
    grammar_rules   = kwa(1,        'grammar_rules')
    verbose         = kwa('none',   'verbose')

    categories = clusters
    log = {'aggregation': aggregation}
    #-if aggregation == 'auto':
    #-    if 'disjuncts' in clusters:
    #-        categories, response = aggregate_jaccard(clusters, 'cats', **kwargs)
    #-    else: categories, response = aggregate_cosine(clusters, **kwargs)
    if aggregation == 'jaccard' or (aggregation == 'auto' and 'disjuncts' in clusters):
        #if dataframe:
        cats = ile_df2cats_dict(clusters)
        #else
        categories, response = aggregate_jaccard(cats, 'cats', **kwargs)
    elif aggregation == 'cosine':
        #-categories, response = aggregate_cosine(clusters, **kwargs)
        df, response = aggregate_cosine(clusters, **kwargs)
        #?categories = ile_df2cats_dict(clusters)
    #-elif aggregation == 'jaccard':
    #-    categories, response = aggregate_jaccard(clusters, 'categories', **kwargs)
    else:
        categories = clusters
        response = {'error': 'aggregate_word_categories - method choice?'}

    log.update(response)
    cats_number = len(set(categories['cluster'].tolist()))
    log.update({'categories': cats_number})
    return categories, log


def generalize_rules(categories, **kwargs):     #80622
    # categories: {'cluster':[], 'words': [], 'disjuncts':[], ...]) from ile_df2cats_dict(clusters)
    def kwa(v,k): return kwargs[k] if k in kwargs else v
    grammar_rules   = kwa(1     ,   'grammar_rules')
    aggregation     = kwa('off' ,   'rules_generalization')
    merge_threshold = kwa(0.8   ,   'rules_merge')
    aggr_threshold  = kwa(0.2   ,   'rules_aggregation')
    verbose         = kwa('none',   'verbose')

    if verbose in ['debug', 'max']:
        print('Jaccard index based generalize_rules')
        if len(set([len(x) for x in categories.values()])) > 1:
            print('cats lengths:', \
                ', '.join([k+':'+str(len(v)) for k,v in categories.items()]))
        else: print('cats lengths:', set([len(x) for x in categories.values()]))

    threshold = merge_threshold # 0.8
    if verbose == 'debug':
        print('generalize_rules: 1st call aggregate with threshold', threshold)
    cats, similarities = aggregate(categories, threshold, jaccard, verbose)
    sims = [x for x in similarities] # if x < threshold]
    threshold = max(sims) - 0.01
    #TODO: list of merged clusters - to delete further?
    #TODO: delete merged clusters

    z = len(similarities)
    while z > 1 and threshold > aggr_threshold:
        cats, similarities = aggregate(cats, threshold, jaccard, verbose)
        sims = [x for x in similarities if x < threshold]
        threshold = max(sims) - 0.01
        if verbose == 'debug':
            print('generalize_rules: call aggregate with threshold', threshold)
            print('⇒ similarities:', similarities, '\n⇒ sims:', sims)
            print('⇒ new threshold:', threshold)
        z = len(sims)

    # Renumber connectors in disjuncts
    if verbose == 'debug': print('generalize_rules: Renumber connectors')
    clusters = [i for i,x in enumerate(cats['cluster']) if i > 0 and x is not None]
    #TODO: all clusters?
    if verbose == 'debug': print('generalize_rules: clusters', clusters)
    sign = lambda x: (1,-1)[x < 0]
    counter = 0

    def ancestor(connector, parents):
        if parents[abs(connector)] == 0:
            return connector
        else: return ancestor(parents[abs(connector)], parents)

    for cluster in clusters:
        new_rule = []
        for disjunct in cats['disjuncts'][cluster]:
            new_dj = []
            for x in disjunct:
                new_dj.append(sign(x) * ancestor(abs(x), cats['parent']))
            new_rule.append(tuple(new_dj))
        cats['disjuncts'][cluster] = set(new_rule)
    return reorder(cats), \
        {'similarity_thresholds': sims, 'updated_disjuncts': counter}


#Notes:

#80725 POC 0.1-0.4 deleted, 0.5 restructured
#80802 poc05.py restructured, cats2list moved to category_learner.py,
    #cats2list copird to poc05.py for tmp compatibility
#TODO: aggregate_cosine - see grammar_learner poc04.
