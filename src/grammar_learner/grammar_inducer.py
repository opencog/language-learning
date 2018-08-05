#language-learning/src/grammar_inducer.py  #80802 poc05.py restructured

def induce_grammar(categories, links, verbose='none'):    #80625 GL POC.0.5
    # categories: {'cluster': [], 'words': [], ...}
    # links: pd.DataFrame (legacy)
    from category_learner import cats2list
    import copy
    if verbose in ['max','debug']:
        print(UTC(),':: induce_grammar: categories.keys():', categories.keys())
    rules = copy.deepcopy(categories)

    clusters = [i for i,x in enumerate(rules['cluster']) if i>0 and x is not None]
    word_clusters = dict()
    for i in clusters:
        for word in rules['words'][i]:
            word_clusters[word] = i

    if verbose in ['max','debug']:
        print('induce_grammar: rules.keys():', rules.keys())
        print('induce_grammar: clusters:', clusters)
        print('induce_grammar: word_clusters:', word_clusters)
        print('induce_grammar: rules ~ categories:')
        display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
            + [x for i,x in enumerate(cats2list(rules)) if i < 4]))

    for cluster in clusters:
        djs = []
        for rule in categories['disjuncts'][cluster]:  #FIXME: categories ⇒ rules 80621
            # 'a- & was-' ⇒ (-9,-26)
            #+TODO? (-x,-y,z) ⇒ (-x,z), (-y,z) ?
            if type(rule) is str:
                x = rule.split()
                dj = []
                for y in x:
                    if y not in ['&', ' ', '']:
                        if y[-1] == '+':
                            dj.append(word_clusters[y[:-1]])
                        elif y[-1] == '-':
                            dj.append(-1 * word_clusters[y[:-1]])
                        else:
                            print('no sign?', dj)  #TODO:ERROR?
                djs.append(tuple(dj))
                if verbose == 'debug':
                    print('induce_gramma: cluster', cluster, '::', rule, '⇒', tuple(dj))
            #TODO? +elif type(rule) is tuple? connectors - tuples?
        rules['disjuncts'][cluster] = set(djs)
        if verbose == 'debug':
            print('induce_grammar: rules["disjuncts"]['+str(cluster)+']', rules['disjuncts'][cluster])
    #rules['djs'] = copy.deepcopy(rules['disjuncts'])  #TODO: check jaccard with tuples else replace with numbers

    if verbose == 'debug':
        print('induce_grammar: updated disjuncts:')
        display(html_table([['Code','Parent','Id','Quality','Words', 'Disjuncts', 'djs','Relevance','Children']] \
            + [x for i,x in enumerate(cats2list(rules)) if i < 32]))

    return rules, {'learned_rules': \
                    len([x for i,x in enumerate(rules['parent']) if x==0 and i>0]), \
                   'total_clusters': len(rules['cluster']) - 1}


#Notes:

#80802 poc05.py restructured: induce_grammar ⇒ grammar_inducer.py v~80625
