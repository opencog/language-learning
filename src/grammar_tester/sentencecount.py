from subprocess import PIPE, Popen
from .commands import *


class SentCountError(Exception):
    pass


def get_sentence_count(corpus_path, options: int) -> int:
    """
    Sentence count routine

    :param corpus_path:     Path to the test text file.
    :param options:         Bit mask representing parsing options.
    :return:                Tuple (ParseMetrics, ParseQuality).
    """
    sentence_count = 0

    sed_cmd = ["sed", "-e", get_sed_regex(options), corpus_path]

    try:
        # Get number of sentences in input file
        with Popen(sed_cmd, stdout=PIPE) as proc_sed, \
             Popen(["wc", "-l"], stdin=proc_sed.stdout, stdout=PIPE, stderr=PIPE) as proc_wcl:

            # Closing grep output stream will terminate it's process.
            proc_sed.stdout.close()

            # Read pipes to get complete output returned by link-parser
            raw, err = proc_wcl.communicate()

            # Check return code to make sure the process completed successfully.
            if proc_wcl.returncode != 0:
                raise SentCountError("Process '{0}' terminated with exit code: {1} "
                                     "and error message:\n'{2}'.".format("wc", proc_wcl.returncode, err.decode()))

            sentence_count = int((raw.decode("utf-8-sig")).strip())

    except KeyboardInterrupt:
        print("get_sentence_count(): Ctrl+C triggered.")
        raise

    except SentCountError as err:
        print("get_sentence_count(): SentCountError: " + str(type(err)) + str(err))

    return sentence_count
