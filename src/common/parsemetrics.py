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
            self.skipped_sentences = int(0)
            self.parse_time = float(0)
        else:
            self.completely_parsed_ratio = other.completely_parsed_ratio
            self.completely_unparsed_ratio = other.completely_unparsed_ratio
            self.average_parsed_ratio = other.average_parsed_ratio
            self.sentences = other.sentences
            self.skipped_sentences = other.skipped_sentences
            self.parse_time = other.parse_time

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
    def parse_time_str(stat) -> str:
        hours = int(stat.parse_time / 3600)
        minutes = int((stat.parse_time - hours * 3600) / 60)
        seconds = int(stat.parse_time % 60)
        millis  = int((stat.parse_time % 60 - seconds) * 1000)
        return "{}h {}m {}s {}ms".format(hours, minutes, seconds, millis)

    @staticmethod
    def text(stat) -> str:
        return  "Total sentences parsed in full:\t\t{}\n" \
                "Total sentences not parsed at all:\t{}\n" \
                "Average sentence parse:\t\t\t{}\n" \
                "Total sentences:\t\t\t{:2.2f}\n" \
                "Skipped sentences:\t\t\t{:2.2f}\n" \
                "Parse time:\t\t\t\t{}\n".format( stat.completely_parsed_str(stat),
                                                      stat.completely_unparsed_str(stat),
                                                      stat.parseability_str(stat),
                                                      stat.sentences,
                                                      stat.skipped_sentences,
                                                      stat.parse_time_str(stat)
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
        self.skipped_sentences += other.skipped_sentences
        self.parse_time += other.parse_time
        return self


class ParseQuality():
    def __init__(self):
        self.total = Decimal('0.00')        # total number of links across all sentences
        self.missing = Decimal('0.00')      # number of missing links across all sentences
        self.extra = Decimal('0.00')        # number of extra links across all sentences
        self.ignored = Decimal('0.00')      # number of ignored links across all sentences
        self.quality = Decimal('0.00')
        self.sentences = Decimal('0.00')    # number of sentences taken into account for F1 calculation
        self.skipped_sentences = int(0)

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
        return "{0:6.4f}".format(stat.recall_val(stat))

    @staticmethod
    def precision_str(stat) -> str:
        return "{0:6.4f}".format(stat.precision_val(stat))

    @staticmethod
    def f1(stat) -> Decimal:
        denominator = stat.recall_val(stat) + stat.precision_val(stat)

        return Decimal("2.00") * stat.recall_val(stat) * stat.precision_val(stat) / denominator \
            if denominator > Decimal("0.0001") else Decimal("0.00")

    @staticmethod
    def f1_str(stat) -> str:
        return "{0:6.4f}".format(stat.f1(stat))

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
        return  "Parse quality:\t{}\n\n" \
                "Average total links:\t{:2.2f}\n" \
                "Average ignored links:\t{:2.2f}\n" \
                "Average missing links:\t{:2.2f}\n" \
                "Average extra links:\t{:2.2f}\n\n" \
                "Recall:\t\t{}\n" \
                "Precision:\t{}\n" \
                "F1:\t\t{}\n\n" \
                "Total sentences:\t{:2.2f}\n" \
                "Skipped sentences:\t{:2.2f}\n".format(
                                                        stat.parse_quality_str(stat),
                                                        stat.avg_total_links(stat),
                                                        stat.avg_ignored_links(stat),
                                                        stat.avg_missing_links(stat),
                                                        stat.avg_extra_links(stat),
                                                        stat.recall_str(stat),
                                                        stat.precision_str(stat),
                                                        stat.f1_str(stat),
                                                        stat.sentences,
                                                        stat.skipped_sentences)

    def __eq__(self, other):
        return  self.quality == other.quality and \
                self.total == other.total and \
                self.ignored == other.ignored and \
                self.missing == other.missing and \
                self.extra == other.extra and \
                self.recall == other.recall and \
                self.precision == other.precision and \
                self.sentences == other.sentences and \
                self.skipped_sentences == other.skipped_sentences

    def __iadd__(self, other):
        self.total += other.total
        self.missing += other.missing
        self.extra += other.extra
        self.ignored += other.ignored
        self.quality += other.quality
        self.sentences += other.sentences
        self.skipped_sentences += other.skipped_sentences

        self.recall += other.recall
        self.precision += other.precision

        return self
