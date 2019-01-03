# language-learning/src/grammar_learner/corpus_stats.py                 # 80831
from collections import Counter


def corpus_stats(lines, extended = False):
    # lines = []
    words = Counter()   # words in sentences
    pws = Counter()     # parsed words in sentences
    npws = Counter()    # non-parsed words
    lefts = Counter()   # left words in links
    rights = Counter()  # right words in links
    links = Counter()   # tuples: (left,right)
    lws = Counter()     # linked words in links

    sentence_lengths = []
    for line in lines:
        if(len(line)) > 1:
            x = line.split()
            if len(x) == 4 and x[0].isdigit() and x[2].isdigit():
                if x[1] != '###LEFT-WALL###' and x[3] != '.':
                    links[(x[1], x[3])] += 1
                    lefts[x[1]] += 1
                    rights[x[3]] += 1
                    lws[x[1]] += 1
                    lws[x[3]] += 1
            elif len(x) > 0:  # sentence:
                sentence_lengths.append(len(x))
                for word in x:
                    if word not in ['###LEFT-WALL###', '.']:
                        if word[0] == '[' and word[-1] == ']':
                            npws[word[1:-1]] += 1   # non-parsed words
                            words[word[1:-1]] += 1
                        else:
                            pws[word] += 1          # parsed words in sentences
                            words[word] += 1
    if len(sentence_lengths) > 0:
        asl = int(round(sum(words.values())/len(sentence_lengths), 0))
    else:
        asl = 0     # average sentence length
    if len(words) > 0:
        awc = int(round(sum(words.values())/len(words), 0))
    else:
        awc = 0     # average word count
    if len(words) > 0:
        apwc = int(round(sum(words.values())/len(words), 0))
    else:
        apwc = 0    # average parsed word count
    if len(links) > 0:
        alc = round(sum(links.values())/len(links), 1)
    else:
        alc = 0     # average link count
    if len(lws) > 0:
        alpw = int(round(sum(links.values())/len(lws), 0))
    else:
        alpw = 0    # average link per word count
    unpws = set(npws) - set(pws)    # unique non-parsed words
    unlws = set(words) - set(lws)   # unique non-linked words
    lost_words = set(words) - (set(lefts)|set(rights))
    # unique words not mentioned in links
    response = {
        'corpus_stats': [
            ['Number of sentences', len(sentence_lengths)],
            ['Average sentence length', asl],
            ['Number of unique words in sentences', len(words)],
            ['Number of unique parsed words in sentences', len(pws)],
            ['Number of unique non-parsed [words] in sentences', len(unpws)],
            ['Number of unique linked words    ', len(lws)],
            ['Number of unique non-linked words', len(unlws)],
            ['Total  words count in sentences', sum(words.values())],
            ['Parsed words count in sentences', sum(pws.values())],
            ['Non-parsed [words] in sentences', sum(npws.values())],
            ['Unique links number', len(links)],
            ['Total  links count ', sum(links.values())],
            ['Average link count ', alc],
            ['Average word count ', apwc],
            ['Average links per linked word', alpw]
        ],
        'links_stats': {
            'unique_left_words': len(lefts),
            'unique_right_words': len(rights),
            'left_&_right_intersection': len(lefts & rights),
            'left_|_right_union': len(lefts | rights),
            'lost_words': len(lost_words),
            'non_parsed|lost_words': len(unpws | lost_words)
        }
    }
    if extended:
        response.update({'unique non-parsed words': unpws,
                         'unique non-linked words': unlws,
                         'lost_words': lost_words, })

    return response


# Notes:

# 80802 poc05 restructured: moved here from pparser.py
# 80829,31 unpws, unlws
# TODO: update - see GitHub issue?
# 81231 cleanup
