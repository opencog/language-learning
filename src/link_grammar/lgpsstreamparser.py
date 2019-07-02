from .lgdatastructures import AbstractLGStreamParser, SentenceParse, Linkage
from ..common.optconst import *
from ..grammar_tester.psparse import *


__all__ = ["LGPSStreamParser", "BreakCycle", "ContinueCycle"]


class BreakCycle(Exception):
    pass


class ContinueCycle(Exception):
    pass


class LGPSStreamParser(AbstractLGStreamParser):
    """
    Link Grammar Postscript Stream Parser
    """
    def __init__(self):
        self._sentence_parses = None

    @staticmethod
    def _parse_batch_ps_output(text: str, options: int, lg_verbosity: int = 1) -> list:
        """
        Parse postscript returned by link-parser executable in a form where each sentence is followed by zero
            or many postscript notated linkages. Postscript linkages are usually represented by three lines
            enclosed in brackets.

        :param text:        String variable with postscript output returned by link-parser.
        :param options:     Parsing options.
        :return:            List of PSSentence.

        """
        sentences = []

        pos = skip_command_response(text)
        end = trim_garbage(text)

        sent_count = 0

        validity_mask = (options & (BIT_EXCLUDE_TIMEOUTED | BIT_EXCLUDE_PANICED | BIT_EXCLUDE_EXPLOSION))

        # Parse output to get sentences and linkages in postscript notation
        for sent in text[pos:end].split("\n\n"):

            sent = sent.strip()

            # Get postscript starting position after parsing LG error and warning messages
            post_start, post_errors = skip_linkage_header(sent)

            # is_valid = post_start >= 0

            # Get input sentence(s) echoed by link-parser
            echo_text = sent if post_start < 0 else sent[:post_start-1]

            # There might be many sentences followed by single postscript if one or several sentences are not parsed
            #   because of so called 'combinatorial explosion'.
            lines = echo_text.split("\n")

            num_lines = len(lines)

            # If verbosity is set to 0
            if lg_verbosity == 0:

                # None of the unparsed by link-parser sentences, if any, should be missed
                for i in range(0, num_lines-1):
                    sent_text = lines[i]
                    tokens = sent_text.split(" ")
                    sent_obj = SentenceParse(sent_text)

                    # Produce fake postscript in order for proper statistic estimation
                    post_text = r"[([" + r"])([".join(tokens) + r"])][][0]"
                    sent_obj.linkages.append(Linkage(post_text))
                    sentences.append(sent_obj)

                sentence = lines[num_lines-1]

            else:
                sentence = lines[0]

            # Check if the postscript linkage is valid
            is_valid = not (post_errors & validity_mask)

            # Successfully parsed sentence is added here
            cur_sent = SentenceParse(sentence)

            cur_sent.valid = is_valid

            postscript = sent[post_start:].replace("\n", "") if is_valid \
                else r"[([" + r"])([".join(sentence.split(" ")) + r"])][][0]"

            cur_sent.linkages.append(Linkage(postscript))
            sentences.append(cur_sent)

            sent_count += 1

        return sentences

    def on_data(self, text: str, options: int):
        """
        Handle link-parser output stream text depending on options' BIT_OUTPUT field.

        :param text:        Stream output text.
        :param options:     Integer variable with multiple bit fields.
        :return:            None
        """
        # Split stream into sentences echoed by link-parser and following linkages in postscript format
        self._sentence_parses = self._parse_batch_ps_output(text, options)

        # Do any additional preparations for parsing postscript
        self.setup()

        # Parse linkages and make statistics estimation
        for sent in self._sentence_parses:

            try:
                # Init sentence-related variables if necessary
                self.on_sentence_init(sent)

                # Parse and calculate statistics for each linkage
                for lnkg in sent.linkages:

                    try:
                        # Init linkage-related variables if necessary
                        self.on_linkage_init(sent, lnkg)

                        # Parse postscript notated linkage and get two lists with tokens and links in return.
                        lnkg.tokens, lnkg.links = parse_postscript(lnkg.linkage_text, options)

                        # Handle fully parsed linkage
                        self.on_parsed_linkage(sent, lnkg)

                        # Update counters or do any necessary cleanup here
                        self.on_linkage_done(sent, lnkg)

                    except BreakCycle:
                        break

                    except ContinueCycle:
                        continue

                self.on_sentence_done(sent)

            except BreakCycle:
                break

            except ContinueCycle:
                continue

        # Do cleanup if necessary
        self.cleanup()
