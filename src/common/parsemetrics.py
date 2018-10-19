from decimal import *

__all__ = ["ParseMetrics", "ParseQuality"]

class ParseMetrics():
    """ Parse statistics data """
    def __init__(self, other=None):

        if other is None:
            self.completely_parsed_ratio = Decimal('0.0')
            self.completely_unparsed_ratio = Decimal('0.0')
            self.average_parsed_ratio = Decimal('0.0')
            self.sentences = int(0)
        else:
            self.completely_parsed_ratio = other.completely_parsed_ratio
            self.completely_unparsed_ratio = other.completely_unparsed_ratio
            self.average_parsed_ratio = other.average_parsed_ratio
            self.sentences = other.sentences

    @staticmethod
    def completely_parsed(stat) -> Decimal:
        if not stat.sentences:
            return Decimal("0")

        return stat.completely_parsed_ratio / stat.sentences * Decimal("100")

    @staticmethod
    def completely_parsed_str(stat) -> str:
        return "{0:6.2f}%".format(stat.completely_parsed(stat))

    @staticmethod
    def completely_unparsed(stat) -> Decimal:
        if not stat.sentences:
            return Decimal("0")

        return stat.completely_unparsed_ratio / stat.sentences * Decimal("100")

    @staticmethod
    def completely_unparsed_str(stat) -> str:
        return "{0:6.2f}%".format(stat.completely_unparsed(stat))

    @staticmethod
    def parseability(stat) -> Decimal:
        if not stat.sentences:
            return Decimal("0")

        return stat.average_parsed_ratio / stat.sentences

    @staticmethod
    def parseability_str(stat) -> str:
        return "{0:6.2f}%".format(stat.parseability(stat) * Decimal("100"))

    @staticmethod
    def text(stat) -> str:
        return  "Total sentences parsed in full:\t\t{}\n" \
                "Total sentences not parsed at all:\t{}\n" \
                "Average sentence parse:\t\t\t{}\n" \
                "Total sentences:\t\t\t{:2.2f}\n".format( stat.completely_parsed_str(stat),
                                                      stat.completely_unparsed_str(stat),
                                                      stat.parseability_str(stat),
                                                      stat.sentences
                                                    )

    def __eq__(self, other):
        return  self.average_parsed_ratio == other.average_parsed_ratio and \
                self.completely_parsed_ratio == other.completely_parsed_ratio and \
                self.completely_unparsed_ratio == other.completely_unparsed_ratio

    def __iadd__(self, other):
        self.completely_parsed_ratio += other.completely_parsed_ratio
        self.completely_unparsed_ratio += other.completely_unparsed_ratio
        self.average_parsed_ratio += other.average_parsed_ratio
        self.sentences += other.sentences
        return self


class ParseQuality():
    def __init__(self):
        self.total = Decimal('0.00')
        self.missing = Decimal('0.00')
        self.extra = Decimal('0.00')
        self.ignored = Decimal('0.00')
        self.quality = Decimal('0.00')
        self.sentences = Decimal('0.00')

        self.recall = Decimal("0.00")
        self.precision = Decimal("0.00")

    @staticmethod
    def recall_val(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.recall / stat.sentences

    @staticmethod
    def precision_val(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.precision / stat.sentences

    @staticmethod
    def recall_str(stat) -> str:
        return "{0:6.2f}%".format(stat.recall_val(stat) * Decimal("100.0"))

    @staticmethod
    def precision_str(stat) -> str:
        return "{0:6.2f}%".format(stat.precision_val(stat) * Decimal("100.0"))

    @staticmethod
    def f1(stat) -> Decimal:
        denominator = stat.recall_val(stat) + stat.precision_val(stat)

        return Decimal("2.00") * stat.recall_val(stat) * stat.precision_val(stat) / denominator \
            if denominator > Decimal("0.0001") else Decimal("0.00")

    @staticmethod
    def f1_str(stat) -> str:
        return "{0:6.2f}%".format(stat.f1(stat) * Decimal('100.0'))

    @staticmethod
    def avg_total_links(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.total / stat.sentences

    @staticmethod
    def avg_ignored_links(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.ignored / stat.sentences

    @staticmethod
    def avg_missing_links(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.missing / stat.sentences

    @staticmethod
    def avg_extra_links(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.extra / stat.sentences

    @staticmethod
    def parse_quality(stat) -> Decimal:
        if not stat.sentences:
            return Decimal('0.00')

        return stat.quality / stat.sentences

    @staticmethod
    def parse_quality_str(stat) -> str:
        return "{0:6.2f}%".format(stat.parse_quality(stat) * Decimal('100.0'))

    @staticmethod
    def text(stat) -> str:
        return  "Parse quality:\t\t{:2.2f}%\n\n" \
                "Average total links:\t{:2.2f}\n" \
                "Average ignored links:\t{:2.2f}\n" \
                "Average missing links:\t{:2.2f}\n" \
                "Average extra links:\t{:2.2f}\n\n" \
                "Recall:\t\t{}\n" \
                "Precision:\t{}\n" \
                "F1:\t\t{}\n\n" \
                "Total sentences: {:2.2f}\n".format(
                                                        stat.parse_quality(stat) * Decimal('100.0'),
                                                        stat.avg_total_links(stat),
                                                        stat.avg_ignored_links(stat),
                                                        stat.avg_missing_links(stat),
                                                        stat.avg_extra_links(stat),
                                                        stat.recall_str(stat),
                                                        stat.precision_str(stat),
                                                        stat.f1_str(stat),
                                                        stat.sentences)

    def __eq__(self, other):
        return  self.quality == other.quality and \
                self.total == other.total and \
                self.ignored == other.ignored and \
                self.missing == other.missing and \
                self.extra == other.extra and \
                self.recall == other.recall and \
                self.precision == other.precision and \
                self.sentences == other.sentences

    def __iadd__(self, other):
        self.total += other.total
        self.missing += other.missing
        self.extra += other.extra
        self.ignored += other.ignored
        self.quality += other.quality
        self.sentences += other.sentences

        self.recall += other.recall
        self.precision += other.precision

        return self
