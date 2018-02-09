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
