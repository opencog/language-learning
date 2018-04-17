#2018-04-11

# Category Learner

def group_links(links, verbose):
    #+TODO: old code ⇒ here  ⇒ src.clustering.group_links.py
    import pandas as pd
    #-Old way:
    from src.link_grammar.turtle import lexical_entries, entries2clusters
    #-djs = links.rename(columns={'link': 'disjunct'})
    #-clusters = entries2clusters(lexical_entries(djs))
    #-entries = lexical_entries(djs)  # 80411:
    if verbose in ['max','debug']:
        print('\ngroup_links: links:\n')
        print(links.sort_values(by='word', ascending=True))
        #with pd.option_context('display.max_rows', 6): print(df2)
    df = links.copy()
    df['links'] = [[x] for x in df['link']]
    del df['link']
    if verbose in ['debug']:
        with pd.option_context('display.max_rows', 6): print(df)
    df = df.groupby('word').agg({'links': 'sum', 'count': 'sum'}).reset_index()
    df['words'] = [[x] for x in df['word']]
    del df['word']
    #-dfm = merge_disjunct_germs(dfg)[['germs', 'disjuncts','counts']]
    #-if verbose == 'max':
    #-    with pd.option_context('display.max_rows', 6): print(df)
    df2 = df.copy().reset_index()
    df2['links'] = df2['links'].apply(lambda x: tuple(sorted(x)))
    #-if verbose == 'max':
    #-    print('\ndf2:\n')
        #with pd.option_context('display.max_rows', 6): print(df2)
    #-    print(df2.sort_values(by='links', ascending=True))

    #-dfq = df2.groupby('links').agg({'words': 'sum', 'count': 'sum'}).reset_index()
    #-if verbose == 'max':
    #-    print('\ndfq:\n')
    #-    with pd.option_context('display.max_rows', 6): print(df3)
    #-ValueError: Names should be list-like for a MultiIndex

    df3 = df2.groupby('links')['count'].apply(sum).reset_index()  #OK
    if verbose == 'debug':
        print('\ndf3:\n')
        with pd.option_context('display.max_rows', 6): print(df3)
    #-df4 = df2.groupby('links')['words'].apply(sum).reset_index()
    #-df4 = df2.copy()
    #-del df4['count']
    df4 = df2.groupby('links')['words'].apply(sum).reset_index()
    #-df5 = df4.groupby('links').agg({'words': 'sum'}).reset_index()
    #-if verbose == 'max':
    #-    print('\ndf4:\n')
    #-    with pd.option_context('display.max_rows', 6): print(df4)
    if df4['links'].tolist() == df3['links'].tolist():
        df4['counts'] = df3['count']
    else:
        print('group_links: linke 53 if df4... == df3... ERROR!')
    df4['links'] = df4['links'].apply(lambda x: list(x))
    #-if verbose == 'max':
    #-    print('\ndf4:\n')
    #-    with pd.option_context('display.max_rows', 6): print(df4)
    #-return df4
    #-dfm = merge_disjunct_germs(dfg)[['germs', 'disjuncts','counts']]
    #-clusters = entries2clusters(entries).rename(columns={'germs': 'cluster_words'})
    df4['words'] = df4['words'].apply(lambda x: sorted(list(x)))
    df4['links'] = df4['links'].apply(lambda x: sorted(list(x)))
    df4 = df4[['words','links','counts']].sort_values(by='words', ascending=True)
    df4.index = ('C' + str(x).zfill(2) for x in range(1, len(df4)+1))
    df4['cluster'] = df4.index  # added 80307 for disjuncts2clusters
    df4 = df4.rename(columns={'words': 'cluster_words', 'links': 'disjuncts'})
    return df4
    #return clusters


def category_learner(links, \
    cat_path, dict_path, tmpath = '', verbose = 'none', \
    parse_mode = 'given', left_wall = '', period = False, \
    context = 1, window = 'mst', weighting = 'ppmi', group = True, \
    word_space = 'vectors', dim_max = 100, sv_min = 0.1,
    dim_reduction = 'svm', \
    clustering = 'kmeans', cluster_range = (2,48,1), \
    cluster_criteria = 'silhouette', cluster_level = 0.9): #, \
    #-generalization = 'off', merge = 0.8, aggregate = 0.2, \
    #-grammar_rules = 1):

    from src.utl.utl import UTC, round1, round2  #, round3, round4, round5
    from src.space.hyperwords import vector_space_dim, pmisvd
    from src.clustering.kmeans import cluster_words_kmeans
    from src.clustering.poc import number_of_clusters, clusters2list
    from src.utl.turtle import html_table, plot2d
    from src.utl.write_files import list2file
    from src.link_grammar.poc import save_link_grammar

    log = {'project': 'Grammar Learner v.0.3 2018-04-11', \
           'date': str(UTC()), 'project_dir': dict_path}
    '''TODO: log: dict ⇒ list [[]]? / OrderedDict?'''

    if tmpath == '': tmpath = dict_path  # temporary files path
    if verbose == 'debug':
        print('category_learner: word_space:', word_space, '/ clustering:', clustering)

    if word_space == 'vectors':
        #^from src.space.hyperwords import vector_space_dim, pmisvd
        dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
        log.update({'vector_space_dim': dim})
        if verbose == 'min': print('Optimal vector space dimensionality:', dim)
        vdf, sv, res3 = pmisvd(links, dict_path, tmpath, dim)
        log.update(res3)
    elif verbose == 'max':
        print('word_space:', word_space, 'clustering:', clustering)

    # Clustering

    if clustering == 'kmeans':
        #^from src.clustering.kmeans import cluster_words_kmeans
        #^from src.clustering.poc import number_of_clusters, clusters2list
        n_clusters = number_of_clusters(vdf, cluster_range ,clustering,  \
            criteria=cluster_criteria, level=cluster_level, verbose=verbose)
        clusters, silhouette, inertia = cluster_words_kmeans(vdf, n_clusters)
        if verbose not in ['min','none']:
            print('Optimal number of clusters:', n_clusters)
        #+if verbose == 'max':
        if verbose in ['max','debug']:        #80413
            print(clusters.applymap(round2))
        if verbose in ['max','debug','mid']:  #80413
            if context == 1:                  #80413 hack :(
                plot2d(1, 2, clusters, 'cluster_words', 10)
            else:
              if len(clusters) < 6:
                  plot2d(1, 3, clusters, 'cluster_words', 10)
              else: plot2d(1, 4, clusters, 'cluster_words', 10)

    elif clustering[:5] in ['group','ident']:  #80406 test ~OK
        if verbose == 'max': print('clustering:', clustering)
        #+from ... import group links
        clusters = group_links(links, verbose)    #80411 new function here - before
        if verbose not in ['min','none']:
            print('Total', len(clusters), \
                'clusters of identical lexical entries', type(clusters))
        if verbose in ['max','debug']:
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

    if verbose in ['debug']:
        print('\nWord categories:\n')
        for line in categories.splitlines()[:3]: print(line)
    if verbose not in ['min','none']:
        print('\nCategory list -', len(categories.splitlines()), 'lines, saved to', cat_file)

    return category_list, log

# Grammar Learner

def clusters2dict(clusters, verbose='none'):
    #_convert clusters versions ⇒ unified dictionary {word: cluster}
    if isinstance(clusters, dict):  #
        return clusters
    elif isinstance(clusters, list): # category_list
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
    if verbose == 'debug': print('\nlinks2stalks\n')
    if isinstance(clusters, dict): word_clusters = clusters
    else: word_clusters = clusters2dict(clusters, verbose)

    def link2links(link):
        if '&' not in link:
            if link[-1] in ['-','+']:
                return word_clusters[link[:-1]] + link[-1]
            else: return link
        else:
            return ' & '.join([word_clusters[x[:-1]] + x[-1] \
                               for x in link.split()if x != '&'])

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
    if verbose == 'debug':
        print('\nstalks:', type(stalks))
        with pd.option_context('display.max_rows', 6): print(stalks, '\n')

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
        #-stalks['disjuncts'] = [[x] for x in stalks['disjuncts']]
        stalks['disjuncts'] = stalks['cluster_links'].apply(relaxed_rules)
        if verbose == 'debug':
            print('links2stalks: connectors ⇒ «relaxed_rules»')
            print('type(stalks["disjuncts"]):', type(stalks['disjuncts']))
    else:
        stalks['disjuncts'] = stalks['cluster_links'].apply(strict_rules)
        if verbose == 'debug':
            print('links2stalks: disjuncts ⇒ strict_rules')
            print('type(stalks["disjuncts"]):', type(stalks['disjuncts']))
    del stalks['cluster_links']
    stalks['words'] = [[x] for x in stalks['word']]
    del stalks['word']

    return stalks


def grammar_learner(clusters, links, grammar_rules = 1, verbose='none'):
    if verbose == 'debug': print('\ngrammar_learner\n')
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

# Learn Grammar = Integration

def learn_grammar(input_dir, \
    cat_path, dict_path, tmpath = '', verbose = 'none', \
    parse_mode = 'given', left_wall = '', period = False, \
    context = 1, window = 'mst', weighting = 'ppmi', group = True, \
    word_space = 'vectors', dim_max = 100, sv_min = 0.1,
    dim_reduction = 'svm', \
    clustering = 'kmeans', cluster_range = (2,48,1), \
    cluster_criteria = 'silhouette', cluster_level = 0.9, \
    generalization = 'off', merge = 0.8, aggregate = 0.2, \
    grammar_rules = 1):
    #80411 replaced 3rd line: learn_mode = 'connectors', context = 1, group = True, \

    import pandas as pd
    from shutil import copy2 as copy
    from src.utl.read_files import check_mst_files
    from src.space.poc import files2links
    #+from src.link_grammar.poc3 import category_learner
    #+from src.link_grammar.poc3 import grammar_learner
    from src.link_grammar.poc import save_link_grammar

    #-links, response = mst2links(input_dir, parse_mode, \
    #-    context, group, left_wall, period, verbose)  # code moved here:
    files, response = check_mst_files(input_dir, verbose)
    # group = True    #? always? False option for context = 0 (words)?
    links, res2 = files2links(files, parse_mode, context, group, \
                              left_wall, period, verbose)
    response.update(res2)
    if verbose == 'debug':
        print('\nfiles2links returns links', type(links), ':\n')
        with pd.option_context('display.max_rows', 6): print(links, '\n')
    #-return links, response  #endof mst2links
    for file in files: copy(file, cat_path)     #80411

    if verbose == 'debug':
        print('learn_grammar: word_space:', word_space, '/ clustering:', clustering)

    category_list, res3 = category_learner(links, \
        cat_path, dict_path, tmpath, verbose, \
        parse_mode, left_wall, period, \
        context, window, weighting, group, \
        word_space, dim_max, sv_min,
        dim_reduction, \
        clustering, cluster_range, \
        cluster_criteria, cluster_level) #, \
        #-generalization = 'off', merge = 0.8, aggregate = 0.2, \
        #-grammar_rules = 1):
    response.update(res3)

    if grammar_rules != context:
        links, res4 = files2links(files, parse_mode, context, group, \
                                  left_wall, period, verbose)

    rule_list, res5 = grammar_learner(category_list, links, grammar_rules, verbose)
    response.update(res5)

    lg_rules_str = save_link_grammar(rule_list, dict_path)
    #TODO: response.update(res6) - res6 from save_link_grammar
    if verbose in ['max','debug']:
        for line in lg_rules_str.splitlines(): print(line)

    return lg_rules_str #0.2.80409 ⇒ #TODO: return response

#_Notes

'''
#80410 code moved into category_learner
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
'''
