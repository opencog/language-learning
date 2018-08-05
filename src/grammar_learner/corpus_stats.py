#language-learning/src/grammar_learner/clustering.py 0.5 80726+80802

def corpus_stats(lines, extended = False):  #80716 #TODO: enhance - issue
    # lines = []
    from collections import Counter
    words = Counter()
    npw = Counter()     #:non-parsed words
    lefts = Counter()   #:left words in links
    rights = Counter()  #:right words in links
    links = Counter()   #:tuples: (left,right)

    sentence_lengths = []
    for line in lines:
        if(len(line)) > 1:
            x = line.split()
            if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                if x[1] != '###LEFT-WALL###' and x[3] != '.':
                    links[(x[1], x[3])] += 1
                    lefts[x[1]] += 1
                    rights[x[3]] += 1
            elif len(x) > 0:  # sentence:
                sentence_lengths.append(len(x))
                for word in x:
                    if word not in ['###LEFT-WALL###', '.']:
                        if word[0] == '[' and word[-1] == ']':
                            npw[word[1:-1]] += 1    #:non-parsed [words] in sentences
                        else: words[word] += 1      #:parsed words in sentences
    if len(sentence_lengths) > 0:
        asl = int(round(sum(words.values())/len(sentence_lengths),0))
    else: asl = 0
    if len(words) > 0:
        apwc = int(round(sum(words.values())/len(words),0))
    else: apwc = 0
    if len(links) > 0:
        aplc = int(round(sum(links.values())/len(links),0))
    else: aplc = 0
    unpw = set(npw) - set(words)    #:unique non-parsed words
    lost_words = set(words) - (set(lefts)|set(rights))  #:unique words not mentioned in links
    response = {
        'corpus_stats': [
            ['Number of sentences', len(sentence_lengths)],
            ['Average sentence length', asl],
            ['Number of unique parsed words in sentences', len(words)],
            ['Number of unique non-parsed [words] in sentences', len(unpw)],
            ['Total words count in sentences', sum(words.values())],
            ['Non-parsed [words] count in sentences', sum(npw.values())],
            ['Average per-word counts', apwc],
            ['Number of unique links', len(links)],
            ['Total links count', sum(links.values())],
            ['Average per-link count', aplc]
        ],
        'links_stats': {
            'unique_left_words': len(lefts),
            'unique_right_words': len(rights),
            'left_&_right_intersection': len(lefts & rights),
            'left_|_right_union': len(lefts | rights),
            'lost_words': len(lost_words),
            'non_parsed|lost_words': len(unpw | lost_words)
        }
    }
    if extended:
        response.update({'lost_words': lost_words, 'unpw': unpw, 'words': set(words)})

    return response


#Notes:

#80802 poc05 restructured: moved here from pparser.py
#TODO: update - see GitHub issue
