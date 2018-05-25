#!/usr/bin/env python3
#/src/utl/widgets.py OpenCog ULL Grammar Learner POC 0.4 80511

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
    plt.figure(figsize=(9,6))     #80413 (9,6) ⇒ (6,4)
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

def category_tree(cat_file, verbose='none'):  # 80522 shortened: display only
    #import os
    from src.utl.turtle import html_table
    from IPython.display import display
    with open(cat_file, 'r') as f: lines = f.read().splitlines()
    #cats = [[y[0], int(y[1]), int(y[2]), y[3], y[4].split(), y[5].split()] \
    cats = [[y[0], int(y[1]), int(y[2]), y[4].split()] \
        for y in [x.split('\t') for x in lines]]  #_shorter: no similarities
    clusters = {}
    m = 0
    for i,x in enumerate(cats):
        if x[0] not in clusters: clusters[x[0]] = []
        clusters[x[0]].append(i)
        if x[2] > m: m = x[2]
    tree = []
    for k,v in clusters.items():
        if len(v) == 1:
            tree.append(cats[v[0]])
        elif len(v) > 1:
            words = []
            similarities = []
            for j in v:
                words.extend(cats[j][3]) #-words.extend(cats[j][4])
                #-similarities.extend(cats[j][5])
            #tree.append([cats[v[0]][0], 0, m+1, cats[v[0]][3], words, similarities])
            tree.append([cats[v[0]][0], 0, m+1, words])
            for j in v:
                #tree.append(['', m+1, cats[j][2], cats[j][3], cats[j][4], cats[j][5]])
                tree.append(['', m+1, cats[j][2], cats[j][3]])
        else: print('WTF?', k, v)
    if verbose not in ['none', 'min']:
        display(html_table([['Code','Parent','Id','Words']] + tree))
    #-Save cat_tree.txt  #80522 ⇒ /src/utl/write_files.py save_category_tree
    #from src.utl.write_files import list2file
    #tree_file = os.path.dirname(cat_file) + '/cat_tree.txt'
    #string = list2file(tree, tree_file)
    return tree


#80511 category tree v.0.1 ~ widget
#80521 html_table, plot_2d copied from utl.turtle.py
#80521 save file
