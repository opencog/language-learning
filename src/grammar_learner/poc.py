#!/usr/bin/env python3
#80331 POC: Proof of Concepf: Grammar Learner 0.1, POC-English-NoAmb

def learn_lexical_entries(input_dir, cat_path, dict_path, verbose='none', \
        parse_mode='given'):
    from IPython.display import display
    from src.utl.turtle import html_table
    from src.utl.read_files import check_dir, check_dir_files, check_corpus
    from src.utl.write_files import list2file
    from src.link_grammar.turtle import \
        files2disjuncts, lexical_entries, entries2clusters, entries2categories, \
        disjuncts2clusters, entries2rules, save_link_grammar

    if check_dir(input_dir, create=False, verbose=verbose):
        files = check_dir_files(input_dir, verbose=verbose)
        if len(files) > 0:
            if verbose == 'max': print(files)
            for i,file in enumerate(files):
                if check_corpus(file, verbose=verbose):
                    if verbose == 'max':
                      print('File #'+str(i), file, 'checked')
                else: print('File #'+str(i), file, 'check failed')
        else: print('Input directory', input_dir, 'is empty')
    else: print('No input directory', input_dir)

    log = {'project': 'Grammar Learner -- Lexical entries'}  # use OR DEL?

    disjuncts = files2disjuncts(files, 'LEFT-WALL', True, verbose)
    #TODO: parse_mode?
    entries = lexical_entries(disjuncts)
    category_list = entries2categories(entries)
    if verbose == 'max':
        display(html_table([['Parent','Category','Quality','Words','Relevance']] + category_list))
    if cat_path[-1] != '/': cat_path += '/'
    cat_file = cat_path + 'categories.txt'
    categories = list2file(category_list, cat_file)
    if verbose == 'max':
        for line in categories.splitlines()[:3]: print(line)
        print('<...>\nTotal', len(categories.splitlines()), 'lines, saved to', cat_file)

    lg_rule_list = entries2rules(disjuncts2clusters(entries2clusters(entries)))
    if verbose == 'max':
        display(html_table([['Cluster','Germs','L','R','Disjuncts']] + lg_rule_list))
    lg_rules_str = save_link_grammar(lg_rule_list, dict_path)
    if verbose == 'max':
        for line in lg_rules_str.splitlines(): print(line)
    #-return categories, lg_rules_dict
    #TODO: return paths to categories and dict?
    s = lg_rules_str.splitlines()[-1]
    lg_file = s[s.find(': ')+2:]
    response = {'categories_file': cat_file, 'grammar_file': lg_file}
    return response

# Connector Learner 80331

def links2stalks(links, clusters):

    word_clusters = dict()
    for row in clusters.itertuples():
        for word in row[2]: word_clusters[word] = row[1]

    def link2links(link):
        if '&' not in link:
            if link[-1] in ['-','+']:
                return word_clusters[link[:-1]] + link[-1]
            else: return link
        else: return None

    df = links.copy()
    df['links'] = df['link'].apply(link2links)
    df['links'] = [[x] for x in df['links']]
    stalks = df.groupby('word').agg({'links': 'sum', 'count': 'sum'}).reset_index()

    stalks['cluster'] = stalks['word'].apply(lambda x: word_clusters[x])
    stalks['[clstr]'] = [[x] for x in stalks['cluster']]
    stalks['cluster_links'] = stalks['[clstr]'] + stalks['links']
    del stalks['[clstr]']
    del stalks['links']

    def relaxed_dj(x):
        lefts = [y for y in x if y[-1] == '-']
        rights = [y for y in x if y[-1] == '+']
        if len(lefts) > 0 and len(rights) > 0:
            left = '{' + ' or '.join([x[0]+y for y in lefts]) + '}'
            right = '{' + ' or '.join([x[0]+y for y in rights]) + '}'
            return left + ' & ' + right
        elif len(lefts) > 0 and len(rights) == 0:
            return ' or '.join([x[0]+y for y in lefts])
        elif len(lefts) == 0 and len(rights) > 0:
            return ' or '.join([x[0]+y for y in rights])
        else: return None

    stalks['disjuncts'] = stalks['cluster_links'].apply(relaxed_dj)
    del stalks['cluster_links']
    stalks['words'] = [[x] for x in stalks['word']]
    del stalks['word']
    stalks['disjuncts'] = [[x] for x in stalks['disjuncts']]
    return stalks


def grammar_learner(clusters, links, verbose='none'):
    from src.utl.turtle import html_table
    stalks = links2stalks(links, clusters)
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
    if verbose == 'max':
       display(html_table([['Cluster','Germs','L','R','Disjuncts']] + rule_list))
    return rule_list


def learn_connectors(input_dir, cat_path, dict_path, verbose='none', \
    parse_mode='given', \
    word_space = 'hyperwords', dim_max = 100, sv_min = 0.1, \
    clustering = 'kmeans', cluster_range = (2,48,1), \
    cluster_criteria = 'silhouette', cluster_level = 0.9, tmpath = ''):

    from src.utl.utl import UTC, round1, round2  #, round3, round4, round5
    from src.utl.read_files import check_mst_files
    from src.space.poc import files2links
    from src.space.hyperwords import vector_space_dim, pmisvd
    from src.clustering.kmeans import cluster_words_kmeans
    from src.clustering.poc import number_of_clusters, clusters2list
    from src.utl.turtle import html_table, plot2d
    from src.utl.write_files import list2file
    from src.link_grammar.poc import save_link_grammar

    log = {'project': 'Unified Grammar Learner: Clustering words', \
           'date': str(UTC()), 'project_dir': dict_path, 'input_dir': input_dir }
    """TODO: dict ⇒ list [[]] / OrderedDict?"""

    files, response = check_mst_files(input_dir, verbose='none')
    links = files2links(files, parse_mode='given', context=1, group = True, \
                        left_wall='LEFT-WALL', period=True, verbose='none')

    # vector_space_dim(links, path, tmpath, dim_max=100, sv_min=0.9, 'max')
    if tmpath == '': tmpath = dict_path
    dim = vector_space_dim(links, dict_path, tmpath, dim_max, sv_min, verbose)
    log.update({'vector_space_dim': dim})
    if verbose not in ['none','min']: print('Optimal vector space dimensionality:', dim)

    vdf, sv, res2 = pmisvd(links, dict_path, tmpath, dim)
    log.update(res2)
    #-vdf.applymap(round2).sort_values(by=[1,2,3], ascending=[False,False,False])

    n_clusters = number_of_clusters(vdf, cluster_range ,clustering,  \
        criteria=cluster_criteria, level=cluster_level, verbose=verbose)
    if verbose not in ['none','min']: print('Optimal number of clusters:', n_clusters)

    clusters, silhouette, inertia = cluster_words_kmeans(vdf, n_clusters)
    if verbose in ['max','debug']: plot2d(1, 2, clusters, 'cluster_words', 10)

    # Generalisation - just histogram? - Grammar-Learner-Clustering-Words 2.6
    import numpy as np
    from src.clustering.similarity import cluster_similarity
    sim_df, res3 = cluster_similarity(clusters, 'max')
    log.update(res3)
    if verbose in ['max','debug']:
      count, division = np.histogram(sim_df['similarity'])
      sim_df['similarity'].hist(bins=division)
      print('Cluster similarities: absolute values > 0.1:')
      sim_df.sort_values(by='similarity', ascending=False).loc[(sim_df['similarity']) > 0.1]

    # Save categories
    category_list = clusters2list(clusters)
    if cat_path[-1] != '/': cat_path += '/'
    cat_file = cat_path + 'categories.txt'
    categories = list2file(category_list, cat_file)
    if verbose in ['max','debug']:
      for line in categories.splitlines(): print(line)
      print('<...>\nTotal', len(categories.splitlines()), \
            'lines, saved to', cat_file)
    #-print(len(categories.splitlines()), 'categories saved to', cat_file)

    # Grammar Learner
    lg_rule_list = grammar_learner(clusters, links, verbose)
    if verbose == 'max':
        display(html_table([['Cluster','Germs','L','R','Disjuncts']] + lg_rule_list))
    lg_rules_str = save_link_grammar(lg_rule_list, dict_path)
    if verbose == 'max':
        for line in lg_rules_str.splitlines(): print(line)
    #-return categories, lg_rules_dict
    #TODO: return paths to categories and dict?
    s = lg_rules_str.splitlines()[-1]
    lg_file = s[s.find(': ')+2:]
    response = {'categories_file': cat_file, 'grammar_file': lg_file}
    return response


# Learn Grammar

def learn_grammar(input_dir, cat_path, dict_path, verbose = 'none', \
    parse_mode = 'given', learn_mode = 'lexical_entries', \
    word_space = 'hyperwords', dim_max = 100, sv_min = 0.1, \
    clustering = 'kmeans', cluster_range = (2,48,1), \
    cluster_criteria = 'silhouette', cluster_level = 0.9, tmpath = ''):

    if learn_mode == 'lexical_entries':
        response = learn_lexical_entries( \
            input_dir, cat_path, dict_path, verbose, parse_mode)
    elif learn_mode == 'connectors_only':
        if tmpath == '': tmpath = dict_path
        response = learn_connectors( \
            input_dir, cat_path, dict_path, verbose, parse_mode,
            word_space, dim_max, sv_min, \
            clustering, cluster_range, cluster_criteria, cluster_level, tmpath)
    #TODO else...
    return response
