from math import log2, log, log10
from typing import Union, Optional, List, Dict

__all__ = ["WordPair", "WordPairs"]

class WordPairError(Exception):
    pass


class WordPair:
    def __init__(self, left: str, right: str):
        self.left: str = left
        self.right: str = right
        self.count: int = 0
        self.minfo: float = float(0.0)


class WordPairs:
    def __init__(self, lcase: bool = True):
        self._lcase = lcase
        self._pairs: Dict[str, WordPair] = dict()
        self._left: Dict[str, (int, float)] = dict()            # dictionary with word count and marginal probability
        self._right: Dict[str, (int, float)] = dict()           # dictionary with word count and marginal probability
        self._word_count: int = 0
        self._pair_count: int = 0

    def _token(self, word: str):
        return word.lower() if self._lcase and not word.startswith(r"###") else word

    def _key(self, left: str, right: str):
        """ Create dictionary key out of two words """
        return self._token(left) + "^^^" + self._token(right)

    def _add_left(self, word: str):
        """ Add word to the dictionary of left words """
        key = self._token(word)
        counter = self._left.get(key, 0)
        self._left[key] = counter + 1

    def _add_right(self, word: str):
        """ Add word to the dictionary of right words """
        key = self._token(word)
        counter = self._right.get(key, 0)
        self._right[key] = counter + 1

    def add(self, left: str, right: str):
        """ Add word pair to pair dictionary and left and right count dictionaries """
        key = self._key(left, right)
        pair = self._pairs.get(key, None)

        if not pair:
            pair = WordPair(self._token(left), self._token(right))
            self._pairs[key] = pair

        word_count = len(self._right) + len(self._left)
        self._add_left(left)
        self._add_right(right)
        increment = len(self._right) + len(self._left) - word_count

        if increment:
            self._word_count += increment

        self._pair_count += 1
        pair.count += 1

    def _left_probability(self, word: str) -> float:
        """ Return left word marginal probability"""
        dict_len = self._pair_count  # len(self._pairs)
        return float(self._left.get(self._token(word), 0)) / float(dict_len) if dict_len else float(0)

    def _right_probability(self, word: str):
        """ Return right word marginal probability """
        dict_len = self._pair_count  # len(self._pairs)
        return float(self._right.get(self._token(word), 0)) / float(dict_len) if dict_len else float(0)

    def _pair_probability(self, left: str, right: str):
        """ Count word pair probability """
        pair = self._pairs.get(self._key(left, right), None)

        if pair is None:
            return float(0)

        dict_len = self._pair_count  # len(self._pairs)

        pair.freq = float(pair.count) / float(dict_len) if dict_len else float(0)

        print(left, right, pair.count, self._pair_count, float(pair.count) / float(self._pair_count))

        return pair.freq

    def _count_pair_mutual_info(self, left: str, right: str):
        """ Count word pair mutual information """

        pair: Optional[WordPair] = self._pairs.get(self._key(left, right), None)

        if pair is None:
            raise WordPairError(f"Word pair '{left}', '{right}' is not found.")

        product = self._left_probability(left) * self._right_probability(right)

        pair_freq = self._pair_probability(left, right)

        # result = ( / product) if product > 0.000000000000001 else float(0)


        # pair.minfo = (-1.4426950408889634 * log(pair_freq) * pair_freq / product) if product > 0.000000000000001 else float(0)


        # pair.minfo = (pair_freq * log2(pair_freq / product)) if product > 0.000000000000001 else float(0)

        pair.minfo = (-log2(pair_freq) / product) if product > 0.000000000000001 else float(0)

        # print(">>", pair.freq, self._left[left][1], self._right[right][1], product, result, log2(result), pair.minfo)

        print(">>", pair_freq, self._left_probability(left), self._right_probability(right), product, log(pair_freq), pair.minfo)

        return pair.minfo

    def count_mi(self):
        print(f"Word count: {self._word_count} Unique Pair Count: {len(self._pairs)} Left: {len(self._left)} Right: {len(self._right)} Total pairs: {self._pair_count}")
        # self.count_probabilities()

        for key, pair in zip(self._pairs.keys(), self._pairs.values()):
            pair.minfo = self._count_pair_mutual_info(pair.left, pair.right)

    def dump(self, stream):
        for pair in self._pairs.values():
            print("{0} {1} {2:2.16f}".format(pair.left, pair.right, pair.minfo), file=stream)
