"""

  REST-API wrapper for Link Grammar parser. Uses Falcon framework along with Gunicorn WSGI server
          (can be any WSGI server).

  Request:
    http://<server ip>:<server port>/linkparser?lang=<language>&text=<sentence>&mode=<mode>&limit=<limit>

              <language>   - short name of the dictionary supported by Link Grammar such as en, ru, tu etc.

              <sentence>   - can be any sentence to be parsed by Link Grammar parser

              <mode>       - numeric output mode. There three modes currently available:

                             0 - graphics (default mode)
                             1 - postscript
                             2 - constituent tree

              <limit>     - maximum number of linkages to return
"""
import falcon
import json
import os
import logging
from linkgrammar import LG_Error, Sentence, ParseOptions, Dictionary
from ull.grammartest import parse_postscript
from ull.grammartest.optconst import *


__version__ = "2.0.0"

# Link Grammar dictionaries root path
LG_DICT_DEFAULT_PATH = "/usr/local/share/link-grammar"

# Log file path to keep track of all requests if necessary
LOG_FILE_PATH = "link-grammar-rest.log"

# Modes of operation
MOD_DIAGRAM         = 0                 # text representation of linkage diagram
MOD_POSTSCRIPT      = 1                 # postscript - linkage tree written in postfix notation
MOD_CONSTTREE       = 2                 # constituent tree
MOD_ULL_SENT        = 3                 # ULL sentence
MAX_MODE_VALUE      = MOD_ULL_SENT
DEFAULT_MODE        = MOD_DIAGRAM

MAX_LINKAGE_LIMIT   = 1000              # maximum linkages restriction
DEFAULT_LIMIT       = 1000              # default number of linkages

DEFAULT_LANGUAGE = "poc-turtle"


def get_ull_sentence(ps_text: str) -> str:
    """
    Extract a sentence from Link Grammar formatted postscript, leaving unparsed words enclosed in square brackets.

    :param ps_text:     Postscript text value.
    :return:            ULL sentence string.
    """
    options = BIT_CAPS | BIT_ULL_NO_LWALL | BIT_STRIP
    tokens, links = parse_postscript(ps_text, options, None)

    num_tokens = len(tokens)

    if num_tokens > 1:
        if tokens[num_tokens-1] == r"###RIGHT-WALL###":
            tokens.remove(r"###RIGHT-WALL###")
            num_tokens -= 1

    return " ".join(tokens[1:]) if len(tokens) > 1 else ""


class LinkParserResource:

    def on_get(self, req, resp):
        """ Handle HTTP GET request """
        link_list               = {}                # output dictionary
        link_list['errors']     = []                # list of errors if any
        link_list['linkages']   = []                # list of linkages in requested format

        try:
            # logging IPs just in case
            logging.info("Connection from: " + (", ".join(req.access_route)))

            # Get input parammeters
            lang    = req.get_param('lang')
            text    = req.get_param('text')
            mode    = req.get_param_as_int('mode')
            limit   = req.get_param_as_int('limit')

            # If no sentence is specified, then nothing to do...
            if text == None:
                logging.debug("Parameter 'text' is not specified. Nothing to parse.")
                raise falcon.HTTPBadRequest("Parameter 'text' is not specified. Nothing to parse.")

            # Use default language if no language is specified
            if lang is None:
                lang = DEFAULT_LANGUAGE
                logging.info("'lang' parameter is not specified in request. 'lang' is set to '" + DEFAULT_LANGUAGE + "'")

            # Use default mode if no or improper value is specified
            if mode is None or mode < 0 or mode > MAX_MODE_VALUE:
                mode = DEFAULT_MODE
                logging.info("'mode' value is not properly specified in request. 'mode' is set to " + str(mode))

            # Use default limit if no value is specified
            #   or value is not within the range [1, MAX_LINKAGE_LIMIT]
            if limit is None or limit < 1 or limit > MAX_LINKAGE_LIMIT:
                limit = DEFAULT_LIMIT
                logging.info("'limit' value is not properly specified in request. 'limit' is set to " + str(limit))

            # Save input parammeters to the output dictionary, just in case someone needs them
            link_list['lang']   = lang
            link_list['mode']   = mode
            link_list['text']   = text
            link_list['limit']  = limit

            # Use default dictionary if it was not explicitly specified
            dict_path = LG_DICT_DEFAULT_PATH + "/" + lang
            dict_path = lang if not os.path.isdir(dict_path) else dict_path

            logging.info("Dictionary path used: " + dict_path)

            # Invoke link-parser, if the parameters are correctly specified
            po = ParseOptions(verbosity=0, min_null_count=0, max_null_count=999)
            po.linkage_limit = limit

            sent = Sentence(text, Dictionary(dict_path), po)
            logging.debug("Sentence: '" + sent.text + "'")

            linkages = sent.parse()

            if mode == MOD_CONSTTREE:
                for linkage in linkages:
                    link_list['linkages'].append(linkage.constituent_tree())

            elif mode == MOD_POSTSCRIPT:
                for linkage in linkages:
                    link_list['linkages'].append(linkage.postscript())

            elif mode == MOD_ULL_SENT:
                    for linkage in linkages:
                        link_list['linkages'].append(get_ull_sentence(linkage.postscript()))

            else:   # MOD_DIAGRAM is default mode
                for linkage in linkages:
                    link_list['linkages'].append(linkage.diagram())

            # Prevent interleaving "Dictionary close" messages
            po = ParseOptions(verbosity=0)

        except LG_Error as err:
            error_msg = "LG_Error: " + str(err)
            link_list["errors"].append(error_msg)
            logging.error(error_msg)

        except Exception as err:
            error_msg = "Exception: " + str(err)
            link_list["errors"].append(error_msg)
            logging.error(error_msg)

        except BaseException as err:
            error_msg = "BaseException: " + str(err)
            link_list["errors"].append(error_msg)
            logging.error(error_msg)

        except:
            error_msg = "Unhandled exception."
            link_list["errors"].append(error_msg)
            logging.error(error_msg)

        # Return proper JSON output
        resp.body = json.dumps(link_list)
        resp.status = falcon.HTTP_200

logging.basicConfig(filename=LOG_FILE_PATH, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

api = falcon.API()
api.add_route('/linkparser', LinkParserResource())
