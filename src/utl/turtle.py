def readmes(file_name):  #80208
    content = {
        'k-means_clusters.txt': \
            'K-means clustering in a range of cluster sizes\n' + \
            'Table columns:\n' + \
            '- N - number of clusters - given K-Means parameter,\n' + \
            '- NR - real number of clusters returned by K-Means,\n' + \
            '- Silhouette - silhouette coefficient, clustering quality metric,\n' + \
            '- Clusters - space delimited, cluster words joined with "+"'
        ,
        'axes_and_clusters_correlation.txt': \
            'Correlation between axes (dimensions) and clusters.\n' + \
            'Table columns:\n' + \
            '- index - word number in the lexicon,\n' + \
            '- 1,2 - word coordinates on axes 1 and 2,\n' + \
            '- cluster - cluster number,\n' + \
            '- c1,c2 - cluster centroid coordinates on axes 1 and 2'
        ,
        'sample.txt': \
            'sample readme text'
        ,  # end of sample readme
        '': 'no readme for empty file name'
    }
    try: return content[file_name]
    except KeyError: return ''


def save_txt_and_readme(tsv, path, file_name, verbose = 'none'):    # 80207
    if '.' not in file_name: file_name = file_name + '.txt'
    # save file:
    with open(path+file_name, 'w') as f: f.write(tsv)
    response = {'saved_file': path+file_name, \
                'readme_file': 'none', 'readme': 'none'}
    if verbose == 'max':
        print('save_txt_and_readme:', path+file_name, 'file saved')
    # save readme:
    try:
        readme = readmes(file_name)
        if readme != '':
            readme_file = path + file_name[:-4] + '_readme.txt'
            readme = readme + '\ndata file: ' + path+file_name
            with open(readme_file, 'w') as f: f.write(readme)
            response['readme_file'] = readme_file
            response['readme'] = readme
            if verbose == 'max':
                print('save_txt_and_readme:', readme_file, 'readme file saved')
        elif verbose == 'max':
            print('save_txt_and_readme error: No readme content for', file_name)
        return response
    except KeyError:
        if verbose == 'max':
            print('save_txt_and_readme error: No readme content for', file_name)
        return response


def html_table(tbl):
    from IPython.display import HTML
    return HTML('<table><tr>{}</tr></table>'
                .format('</tr><tr>'
                        .join('<td>{}</td>'
                              .format('</td><td>'
                                      .join(str(_) for _ in row)) for row in tbl)))


def plot2d(i, j, df, label='', f=15):   # 80216
    import matplotlib.pyplot as plt
    if type(label) == str and label != '':
        if label == 'cluster_words':
            header = 'Cluster words'
        else: header = 'Words'
        print(header, 'in vector space, axes', i, 'and', j)
    font = {'size': f}
    plt.rc('font', **font)
    plt.figure(figsize=(9,6))
    plt.scatter(df[i].values, df[j].values)
    #plt.axis('off')
    plt.xlim(round(df[i].min()-0.2,1), round(df[i].max()+0.1,1))
    plt.ylim(round(df[j].min()-0.1,1), round(df[j].max()+0.2,1))
    k = df.index.min()  # ~ 1st row index (usually 0 or 1)
    for n, wlst in enumerate(df[label]):
        x, y = df[i][n+k], df[j][n+k]
        plt.scatter(x, y)
        annot = {'has': (1, 50), 'is': (1, 5)}
        plt.annotate(wlst, xy=(x, y),
            xytext=annot.get(' '.join(w for w in wlst),(1+n*2, 6*n)),
            textcoords='offset points', ha='right', va='bottom', )
    #plt.show()
