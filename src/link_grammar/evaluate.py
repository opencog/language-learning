__all__ = ['Load_File', 'Get_Parses', 'MakeSets', 'Evaluate_Parses']


def Load_File(filename):
    """
        Loads a data file
    """
    with open(filename) as file:
        data = file.readlines()
    return data


def Get_Parses(data, ignore_wall=True):
    """
        Separates parses from data into format:
        [
          [[sentence-parse1][link1-parse1][link2-parse1] ... ]
          [[sentence-parse2][link1-parse2][link2-parse2] ... ]
          ...
        ]
        Each list is splitted into tokens using space.

        Token renumeration added. Works only when ignore_wall=True.
    """
    parses = []
    parse_num = -1
    new_flag = True

    links_skipped = 0

    for line in data:

        if line == "\n":
            new_flag = True
            continue

        if new_flag:
            parse_num += 1
            new_flag = False
            parses.append([[(((line.replace("[", "")).replace("]", "")).replace("\n", "")).strip()]])
            links_skipped = 0
            continue

        parse = line.split()

        assert len(parse) == 4

        if ignore_wall and (parse[1] == "." or parse[3] == "."
                            or parse[1].startswith(r"###") or parse[3].startswith(r"###")):
            links_skipped += 1
            continue

        new_parse = []

        for i, element in zip(range(len(parse)), parse):
            new_element = element if (i & 1) else int(element)  # - links_skipped
            new_parse.append(new_element)

        # print(new_parse)
        parses[parse_num].append(new_parse)

    parses.sort()

    # print(parses)

    return parses


# def Get_Parses(data, ignore_wall=True):
#     """
#         Separates parses from data into format:
#         [
#           [[sentence-parse1][link1-parse1][link2-parse1] ... ]
#           [[sentence-parse2][link1-parse2][link2-parse2] ... ]
#           ...
#         ]
#         Each list is splitted into tokens using space.
#
#         Token renumeration added. Works only when ignore_wall=True.
#     """
#     parses = []
#     parse_num = -1
#     new_flag = True
#
#     links_skipped = 0
#
#     for line in data:
#
#         if line == "\n":
#             new_flag = True
#             continue
#
#         if new_flag:
#             parse_num += 1
#             new_flag = False
#             parses.append([[(((line.replace("[", "")).replace("]", "")).replace("\n", "")).strip()]])
#             links_skipped = 0
#             continue
#
#         parse = line.split()
#
#         assert len(parse) == 4
#
#         if ignore_wall and (parse[1] == "." or parse[3] == "."
#                             or parse[1].startswith(r"###") or parse[3].startswith(r"###")):
#             links_skipped += 1
#             continue
#
#         new_parse = []
#
#         for i, element in zip(range(len(parse)), parse):
#             new_element = element if (i & 1) else int(element) - links_skipped
#             new_parse.append(new_element)
#
#         # print(new_parse)
#         parses[parse_num].append(new_parse)
#
#     parses.sort()
#
#     # print(parses)
#
#     return parses


def MakeSets(parse):
    """
        Gets a list with links (without full sentence) and
        and makes sets for each link's ids
    """
    link_sets = [{(link[0], link[1]), (link[2], link[3])} for link in parse]
    return link_sets

def Evaluate_Parses(test_parses, ref_parses, verbose, ignore, ofile):
    """
        Compares test_parses against ref_parses link by link
        counting errors
    """
    total_links = 0     # in gold standard
    #extra_links = 0     # links present in test, but not in ref
    missing_links = 0   # links present in ref, but not in test
    ignored_links = 0   # ignored links, if ignore is active

    for ref_parse, test_parse in zip(ref_parses, test_parses):
        current_missing = 0
        ref_sent = ref_parse.pop(0)[0].split()
        test_sent = test_parse.pop(0)[0].split()

        if ref_sent != test_sent:
            print(ref_sent, file=ofile)
            print(test_sent, file=ofile)
            print("Error: files don't contain same parses", file=ofile)

            print(ref_sent)
            print(test_sent)
            print("Error: files don't contain same parses")
            return

        ref_sets = MakeSets(ref_parse)  # using sets to ignore link directions
        test_sets = MakeSets(test_parse)
        sent_length = str(len(ref_sent))

        # loop over every ref link and try to find it in test
        for ref_link in ref_sets:
            if ignore:
                if (('0', '###LEFT-WALL###') in ref_link) or ((sent_length, ".") in ref_link):
                    ignored_links += 1
                    continue
            total_links += 1
            if ref_link in test_sets:
                test_sets.remove(ref_link)
            else:
                current_missing += 1 # count links not contained in test

        if verbose:
            print("Sentence: {}".format(" ".join(ref_sent)), file=ofile)
            print("Missing links: {}".format(current_missing), file=ofile)
            print("Extra links: {}".format(len(test_sets)), file=ofile)

        #extra_links += len(test_sets) # count links not contained in reference
        missing_links += current_missing

    score = 1 - missing_links / total_links
    print("\nParses score: {0:2.2f}".format(score*100.0), file=ofile)
    print("A total of {} links".format(total_links), file=ofile)
    print("A total of {} ignored links".format(ignored_links), file=ofile)
    print("A total of {} missing links".format(missing_links), file=ofile)
    #print("A total of {} extra links".format(extra_links))
