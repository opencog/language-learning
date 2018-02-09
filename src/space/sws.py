import numpy as np
import pandas as pd

def singular_word_space(df, verbose='none'):  #80202
    # Create singular word space from word pairs: (a,b) => (a,b+), (b,a-)
    lefts = df.copy()
    lefts['word1'] = lefts['word1'] + '-'
    lefts = lefts.rename(columns={'word1':'link', 'word2':'word'})
    rights = df.copy()
    # del df to free RAM - impossible? :( - don't make rights copy?
    rights['word2'] = rights['word2'] + '+'
    rights = rights.rename(columns={'word1':'word', 'word2':'link'})
    links = pd.concat([lefts, rights], axis=0, ignore_index=True) \
        .groupby(['word','link'], as_index=False).sum() \
        .sort_values(by=['count','word','link'], ascending=[False,True,True]) \
        .reset_index(drop=True)
    if verbose not in ['none', 'min']:
        print('Singular word space links:', len(lefts), 'left words,', \
              len(rights), 'right words,', len(links), 'pairs')
    if verbose == 'max':
        with pd.option_context('display.max_rows', 6):
            print('Merged links:\n', links, '\n')
    return links


def word_space(links, path, prefix, verbose='none'):  #80202
    # Count words and contexts
    words = links.groupby('word').sum().reset_index() \
        .sort_values(by=['count','word'], ascending=[False,False])
    contexts = links.groupby('link').sum().reset_index() \
        .sort_values(by=['count','link'], ascending=[False,False])
    if verbose != 'none':
      print('Word space:', len(words), 'words,', len(contexts), 'contexts (dependent words)')
    if verbose == 'max':
        print('\nSorted words:', len(words), 'items')
        with pd.option_context('display.max_rows', 6): print(words,'\n')
        print('Sorted_contexts:', len(contexts), 'items')
        with pd.option_context('display.max_rows', 6): print(contexts,'\n')
    # Save results
    lf = prefix + 'wordspace.tsv'
    wf = prefix + 'wordspace_words.tsv'
    cf = prefix + 'wordspace_context.tsv'
    links.to_csv(path+lf, header=True, index=False, sep='\t')
    words.to_csv(path+wf, header=True, index=False, sep='\t')
    contexts.to_csv(path+cf, header=True, index=False, sep='\t')
    readme_file = path + prefix + 'wordspace_readme.tsv'
    readme = 'Wordspace files:\n'+ \
        '- '+lf+' - word space - '+str(len(links))+' links (word pairs)\n'+ \
        '- '+wf+' - lexicon: words and frequencies ('+str(len(words))+' items)\n'+\
        '- '+cf+' - dependent words in links ('+str(len(contexts))+' items)\n'+\
        'Path: '+path
    with open(readme_file, 'w') as f: f.write(readme)
    # Print comments:
    if verbose == 'max':
        print('Words space saved to:', path, '\n', \
            '- links file -', len(links), 'links -', lf, '\n', \
            '- lexicon - ', len(words), 'words -', wf, '\n', \
            '- context - ', len(contexts), 'context (dependent) words -', cf, '\n')
    elif verbose == 'max':
        print('Words space, word & context counts saved to:\n', \
            path+lf+',\n', wf+',', cf)
    # Return
    response = { 'links': len(links) ,'words': len(words), \
        'contexts': len(contexts), 'links_file': path+lf, \
        'lexicon_file': path+wf, 'context_file': path+cf }
    return words, contexts, response
