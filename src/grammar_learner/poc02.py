#2018-04-06



def mst2links(input_dir, parse_mode, context=1, group=True, \
              left_wall='', period=False, verbose='none'):
    import pandas as pd
    from src.utl.read_files import check_mst_files
    from src.space.poc import files2links
    files, response = check_mst_files(input_dir, verbose='none')
    #-if verbose == 'max': print('Response', response)

    # Input data

    #^from src.space.poc import files2links
    #context = 1     #= 'connectors'
    #context = 9     #= 'disjuncts'
    group = True    #? always? False option for context = 0 (words)
    links, res2 = files2links(files, parse_mode, context, group, \
                                  left_wall, period, verbose)
    #-if verbose == 'max': print('res2:', res2)
    response.update(res2)
    if verbose == 'max':
        print('\nmst2links returns links', type(links), ':\n')
        with pd.option_context('display.max_rows', 6): print(links)
    return links, response


def category_learner(links, \
    cat_path, dict_path, verbose='none', \
    parse_mode='given', \
    word_space = 'vectors', dim_max = 100, sv_min = 0.1, \
    dim_reduction = 'svm', \
    clustering = 'kmeans', cluster_range = (2,48,1), \
    cluster_criteria = 'silhouette', cluster_level = 0.9, tmpath = '',
    generalization = 'off',
    grammar_rules = 'connectors'):  # no actual need need for grammar rules here?

    from src.utl.utl import UTC, round1, round2  #, round3, round4, round5
    from src.space.hyperwords import vector_space_dim, pmisvd
    from src.clustering.kmeans import cluster_words_kmeans
    from src.clustering.poc import number_of_clusters, clusters2list
    from src.utl.turtle import html_table, plot2d
    from src.utl.write_files import list2file
    from src.link_grammar.poc import save_link_grammar

    log = {'project': 'Grammar Learner v.0.2 2018-04-06', \
           'date': str(UTC()), 'project_dir': dict_path}

    '''TODO: log: dict ⇒ list [[]]? / OrderedDict?'''

    if word_space == 'vectors':
        if tmpath == '': tmpath = dict_path
        #^from src.space.hyperwords import vector_space_dim, pmisvd
        dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        log.update({'vector_space_dim': dim})
        if verbose == 'min': print('Optimal vector space dimensionality:', dim)
        vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        log.update(res3)
    else:
        #TODO: word_space = 'discrete'...
        if tmpath == '': tmpath = dict_path
        dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        log.update({'vector_space_dim': dim})
        if verbose == 'min': print('Optimal vector space dimensionality:', dim)
        vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        log.update(res3)

    # Clustering
    #-clustering = 'group'

    if clustering == 'kmeans':
        #^from src.clustering.poc import number_of_clusters, clusters2list
        n_clusters = number_of_clusters(vdf, cluster_range ,clustering,  \
            criteria=cluster_criteria, level=cluster_level, verbose=verbose)
        clusters, silhouette, inertia = cluster_words_kmeans(vdf, n_clusters)
        if verbose not in ['min','none']:
            print('Optimal number of clusters:', n_clusters)
        if verbose == 'max': plot2d(1, 2, clusters, 'cluster_words', 10)

    elif clustering[:5] in ['group', 'ident']:  #80606 test ~OK
        def group_links(links):
            #+TODO: old code ⇒ here  ⇒ src.clustering.group_links.py
            #-Old way:
            from src.link_grammar.turtle import lexical_entries, entries2clusters
            djs = links.rename(columns={'link': 'disjunct'})
            #-clusters = entries2clusters(lexical_entries(djs))
            entries = lexical_entries(djs)
            clusters = entries2clusters(entries).rename(columns={'germs': 'cluster_words'})
            return clusters
        #+from ... import group links
        clusters = group_links(links)
        if verbose not in ['min','none']:
            print('Total', len(clusters), \
                'clusters of identical lexical entries', type(clusters))
        if verbose == 'max':
            print('\n', clusters[['cluster_words', 'disjuncts']]) #.head(12))

    # Generalization  #TODO next week

    # Save categories

    #^from src.clustering.poc import clusters2list
    #^from src.utl.write_files import list2file
    category_list = clusters2list(clusters)
    if verbose not in ['min','none']:
        display(html_table([['Parent','Category','Quality','Words','Relevance']] \
            + category_list))

    '''TODO: categories file name'''

    if cat_path[-1] != '/': cat_path += '/'
    cat_file = cat_path + 'categories.txt'
    categories = list2file(category_list, cat_file)

    '''TODO: category file path ⇒ log'''

    if verbose == 'max':
        for line in categories.splitlines()[:3]: print(line)
    if verbose != 'none':
        print('<...>\nTotal', len(categories.splitlines()), 'lines, saved to', cat_file)

    return category_list, log


def clusters2dict(clusters, verbose='none'):
    #_convert clusters versions ⇒ unified dictionary {word: cluster}
    if isinstance(clusters, dict):  #
        return clusters
    elif isinstance(clusters, list): # category_list
        print('list')
        d = dict()
        for row in clusters:
            for word in row[3]: d[word] = row[1]
        return d
    if isinstance(clusters, pd.DataFrame):
        if 'germs' in clusters:
            d = dict()
            for row in clusters.itertuples():
                for word in row[1]: d[word] = row[4]
            if verbose == 'max': print('germs!')
            return d
        else:
            d = dict()
            for row in clusters.itertuples():
                for word in row[2]: d[word] = row[1]
            if verbose == 'max': print('no germs')
            return d

def links2stalks(links, clusters, grammar_rules = 1, verbose='none'):
    # grammar_rules: 'connectors', 'disjuncts'
    if isinstance(clusters, dict): word_clusters = clusters
    else: word_clusters = clusters2dict(clusters, verbose)

    def link2links(link):
        if '&' not in link:
            if link[-1] in ['-','+']:
                return word_clusters[link[:-1]] + link[-1]
            else: return link
        else:
            return ' & '.join([word_clusters[x[:-1]] + x[-1] for x in link.split()if x != '&'])

    df = links.copy()
    df['links'] = df['link'].apply(link2links)
    df['links'] = [[x] for x in df['links']]
    stalks = df.groupby('word').agg({'links': 'sum', 'count': 'sum'}).reset_index()
    #-stalks['links'] = stalks['links'].apply(dedupe)
    stalks['links'] = stalks['links'].apply(lambda x: sorted(set(x)))

    stalks['cluster'] = stalks['word'].apply(lambda x: word_clusters[x])
    #-print(stalks.head(3))
    stalks['[clstr]'] = [[x] for x in stalks['cluster']]
    stalks['cluster_links'] = stalks['[clstr]'] + stalks['links']
    del stalks['[clstr]']
    del stalks['links']
    print(stalks.head(3))

    def relaxed_rules(x):  # (c) Anton: ({a- or b-} & {c+ or d+}) or ({a-} & {c+})
        #TODO: split disjuncts? OR just ignore?
        #-lefts = [y for y in x if y[-1] == '-']    #80331
        #-rights = [y for y in x if y[-1] == '+']   #80331
        z = [y for y in x[1:] if '&' not in y]      #80405 ignore disjuncts - nicht gut?
        lefts = sorted(set([y for y in z if y[-1] == '-']))      #80405
        rights = sorted(set([y for y in z if y[-1] == '+']))     #80405
        disjuncts = []
        if len(lefts) > 0 and len(rights) > 0:
            left = '{' + ' or '.join([y[:-1]+x[0]+'-' for y in lefts]) + '}'
            right = '{' + ' or '.join([x[0]+y for y in rights]) + '}'
            disjuncts.append(left + ' & ' + right)
        elif len(lefts) > 0 and len(rights) == 0:
            disjuncts.append(' or '.join([y[:-1]+x[0]+'-' for y in lefts]))
        elif len(lefts) == 0 and len(rights) > 0:
            disjuncts.append(' or '.join([x[0]+y for y in rights]))
        return disjuncts

    def strict_rules(x):
        disjuncts = []
        for y in x[1:]:
            if '&' in y:
                def f(z):  #! inside only: not pure - uses scope x[0] :(
                    if z[-1] == '-':
                        return z[:-1] + x[0] + '-'
                    else: return x[0] + z
                disjuncts.append(' & '.join([f(z) for z in y.split() if z != '&']))
            elif y[-1] == '-':
                disjuncts.append(y[:-1]+x[0]+'-')
            elif y[-1] == '+':
                disjuncts.append(x[0]+y)
        disjuncts = list(set(disjuncts))
        disjuncts.sort()
        return list(set(disjuncts))

    if grammar_rules == 1:
        if verbose == 'max': print('links2stalks: connectors ⇒ «relaxed_rules»')
        stalks['disjuncts'] = stalks['cluster_links'].apply(relaxed_rules)
        #-stalks['disjuncts'] = [[x] for x in stalks['disjuncts']]
    else:
        if verbose == 'max': print('links2stalks: disjuncts ⇒ strict_rules')
        stalks['disjuncts'] = stalks['cluster_links'].apply(strict_rules)
        print('type(stalks["disjuncts"]):', type(stalks['disjuncts']))
    del stalks['cluster_links']
    stalks['words'] = [[x] for x in stalks['word']]
    del stalks['word']

    return stalks


def grammar_learner(clusters, links, grammar_rules = 1, verbose='none'):
    #?import links2stalks
    from src.utl.turtle import html_table

    stalks = links2stalks(links, clusters, grammar_rules, verbose)
    rules = stalks.groupby('cluster') \
        .agg({'words': 'sum', 'disjuncts': 'sum', 'count': 'sum'}).reset_index()
    rule_list = list()
    for row in rules.itertuples():
        rule = []
        rule.append(row[1])     # Cluster
        rule.append(row[2])     # Words
        rule.append([])         # Left Connectors
        rule.append([])         # Right Connectors
        rule.append(row[3])     # Disjuncts
        rule_list.append(rule)
    rule_list.sort()
    if verbose not in ['min','none']:
       display(html_table([['Cluster','Germs','L','R','Disjuncts']] + rule_list))

    return rule_list, {'rule_list': len(rule_list)}


def learn_grammar(input_dir, cat_path, dict_path, verbose='none', \
    parse_mode='given', \
    context = 1, group = True, left_wall = '', period = False, \
    word_space = 'vectors', dim_max = 100, sv_min = 0.1, \
    dim_reduction = 'svm', \
    clustering = 'kmeans', cluster_range = (2,48,1), \
    cluster_criteria = 'silhouette', cluster_level = 0.9, tmpath = '',
    generalization = 'off', grammar_rules = 1):

    from src.link_grammar.poc import save_link_grammar

    links, response = mst2links(input_dir, parse_mode, \
        context, group, left_wall, period, verbose)

    category_list, res2 = category_learner(links, \
    cat_path, dict_path, verbose, \
    parse_mode, word_space, dim_max, sv_min, dim_reduction, \
    clustering, cluster_range, cluster_criteria, cluster_level, tmpath,
    generalization, grammar_rules)

    if grammar_rules != context:
        links, response = mst2links(input_dir, parse_mode, \
            grammar_rules, group, left_wall, period, verbose)

    rule_list, res3 = grammar_learner(category_list, links, grammar_rules, verbose)

    lg_rules_str = save_link_grammar(rule_list, dict_path)
    if verbose == 'max':
        for line in lg_rules_str.splitlines(): print(line)

    response.update(res2)
    response.update(res3)
    #TODO: res4 from save_linki_grammar
    return lg_rules_str #response
