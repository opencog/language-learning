from ..link_grammar.lgdatastructures import PQSentenceParse, Linkage
from ..link_grammar.lgpsstreamparser import LGPSStreamParser, BreakCycle
from .wordpairs import WordPairs


class LGPSTokenizer(LGPSStreamParser):

    def __init__(self, pairs: WordPairs, num_linkages: int=1):
        super().__init__()

        self._pairs = pairs
        self._sentence_count = 0
        self._num_linkages = num_linkages

    def setup(self):
        self._sentence_count = 0

    def cleanup(self):
        # self._pairs.count_mi()
        pass

    def on_sentence_init(self, sentence: PQSentenceParse):
        sentence.linkage_count = 0

    def on_sentence_done(self, sentence: PQSentenceParse):
        self._sentence_count += 1

    def on_linkage_init(self, sentence: PQSentenceParse, linkage: Linkage):
        if sentence.linkage_count == self._num_linkages:
            raise BreakCycle()
        # pass

    def on_parsed_linkage(self, sentence: PQSentenceParse, linkage: Linkage):
        print(linkage.linkage_text)

        for link in linkage.links:
            # if linkage.tokens[link[0]] == r"###LEFT-WALL###":  # and linkage.tokens[link[1]] == r".":
                # print("{} {}".format(linkage.tokens[link[0]], linkage.tokens[link[1]]))

            self._pairs.add(linkage.tokens[link[0]], linkage.tokens[link[1]])

    def on_linkage_done(self, sentence: PQSentenceParse, linkage: Linkage):
        pass
