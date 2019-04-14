# language-learning/src/grammar_learner/widgets.py                      # 80817
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from .utl import kwa, UTC
from .read_files import check_dir, check_mst_files
from .pparser import files2links


def html_table(tbl):
    return HTML('<table><tr>{}</tr></table>'
                .format('</tr><tr>'
                        .join('<td>{}</td>'
                              .format('</td><td>'
                                      .join(str(_) for _ in row))
                              for row in tbl)))


def plot2d(i, j, df, label='', f=15):
    if type(label) == str and label != '':
        if label == 'cluster_words':
            header = 'Cluster words'
        else: header = 'Words'
        print(header, 'in vector space, axes', i, 'and', j)
    font = {'size': f}
    plt.rc('font', **font)
    plt.figure(figsize=(9, 6))
    plt.scatter(df[i].values, df[j].values)
    # plt.axis('off')
    plt.xlim(round(df[i].min()-0.2,1), round(df[i].max()+0.1,1))
    plt.ylim(round(df[j].min()-0.1,1), round(df[j].max()+0.2,1))
    k = df.index.min()  # ~ 1st row index (usually 0 or 1)
    for n, wlst in enumerate(df[label]):
        x, y = df[i][n+k], df[j][n+k]
        plt.scatter(x, y)
        annot = {'has': (1, 50), 'is': (1, 5)}
        plt.annotate(wlst, xy=(x, y),
            xytext = annot.get(' '.join(w for w in wlst), (1+n*2, 6*n)),
            textcoords = 'offset points', ha='right', va='bottom', )
    # plt.show()


def category_tree(cat_file, verbose='none'):
    with open(cat_file, 'r') as f:
        lines = f.read().splitlines()
    cats = [[y[0], int(y[1]), int(y[2]), y[4].split()]
            for y in [x.split('\t') for x in lines]]  # shorter: no similarities
    clusters = {}
    m = 0
    for i, x in enumerate(cats):
        if x[0] not in clusters:
            clusters[x[0]] = []
        clusters[x[0]].append(i)
        if x[2] > m:
            m = x[2]
    tree = []
    for k, v in clusters.items():
        if len(v) == 1:
            tree.append(cats[v[0]])
        elif len(v) > 1:
            words = []
            similarities = []
            for j in v:
                words.extend(cats[j][3])
            tree.append([cats[v[0]][0], 0, m+1, words])
            for j in v:
                tree.append(['', m+1, cats[j][2], cats[j][3]])
        else:
            print('WTF?', k, v)
    #  TODO: To be reviewed and changed if necessary
    if verbose not in ['none', 'min']:
        display(html_table([['Code', 'Parent', 'Id', 'Words']] + tree))

    return tree


def display_tree(response):
    print('Parse ability (PA), parse quality(PQ), PA*PQ:',
          str(response['parse_ability']) + '%, ' +
          str(response['parse_quality']) + '%, ' +
          str(response['parse_quability']) + '%;')
    print('Category tree "cat_tree.txt" file:')
    with open(response['cat_tree_file'], 'r') as f:
        x = f.read().splitlines()
    display(html_table([y.split('\t') for y in x]))


def corpus_histograms(module_path, corpus, dataset,
                      logscale=[False,False], **kwargs):
    parse_mode      = kwa('lower',  'parse_mode', **kwargs)    # 'casefold'
    input_parses = module_path + '/' + corpus + '/' + dataset
    files, re01 = check_mst_files(input_parses, kwargs['verbose'])
    kwargs['input_files'] = files
    kwargs['context'] = 1
    ordnung = ['word', 'link', 'count']
    links, re02 = files2links(**kwargs)
    connectors = links[ordnung]
    for x in re02['corpus_stats']:
        print(x[0], ':', x[1])
    kwargs['context'] = 2
    links, re02 = files2links(**kwargs)
    disjuncts = links[ordnung]

    words = connectors.groupby('word', as_index=False).sum()['count']
    cons = connectors.groupby('link', as_index=False).sum()['count']
    con_seeds = connectors.groupby(['word', 'link'], as_index=False) \
        .sum()['count']
    djs = disjuncts.groupby('link', as_index=False).sum()['count']
    seeds = disjuncts.groupby(['word','link'], as_index=False).sum()['count']

    fig, ax = plt.subplots()
    n, bins, patches = ax.hist([words, cons], label=['words', 'connectors'],
                               alpha=0.5, histtype='bar', log=logscale[0])
    # ax.set_xlabel('Count')
    # ax.set_ylabel('Frequency')
    title = 'Words, connectors Frequency'
    if logscale[0]:
        title = title + ', log scale'
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    plt.show()

    fig2, ax2 = plt.subplots()
    n, bins, patches = ax2.hist([djs, seeds], label=['disjuncts', 'seeds'],
                                color=['blue','red'], alpha=0.5,
                                histtype='bar', log=logscale[1])
    title = 'Disjuncts, seeds frequency'
    if logscale[1]:
        title = title + '; Y: log scale'
    ax2.legend()
    ax2.set_title(title)
    fig2.tight_layout()
    plt.show()


# Notes:

# 80511 category tree v.0.1 ~ widget
# 80521 html_table, plot_2d copied from utl.turtle.py
# 80521 save file
# 80627 display_tree  FIXME:DEL?
# 80817 corpus_histograms ⇒ ? FIXME:DEL?
# 81231 cleanup
