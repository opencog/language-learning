#!/usr/bin/env python3

"""

    This library is intended to simpify the use of localy installed Link Grammar API and Link Grammar REST API.
    Class wrapper allows to use both with the same set of methods and handle parsing results the same way.

"""

__all__     = [
                'LGClientError', 'LGClient', 'LGClientCallback', 'LGClientLib', 'LGClientREST', 'LGClientCallback',
                'get_lg_client'
              ]

__version__ = '0.1'

import sys
# import re, os, shutil, locale, getopt
from linkgrammar import LG_Error, LG_DictionaryError, Linkage, Sentence, ParseOptions, Dictionary, Clinkgrammar as clg
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse
import json

"""
    Exception class for all Link Grammar clients

"""
class LGClientError(Exception):

    def __init__(self, err_msg, err_code):
        self._err_msg = err_msg
        self._err_code = err_code

    def __str__(self):
        return self._err_msg

"""
    Abstract class defines callback interface
"""
class LGClientCallback(metaclass=ABCMeta):

    @abstractmethod
    def on_linkages(self, linkages):
        pass

    @abstractmethod
    def on_linkage(self, linkage):
        pass

    @abstractmethod
    def on_link(self, link):
        pass

"""
    Base class for all Link Grammar clients
"""
class LGClient(metaclass=ABCMeta):

    """ Gets/sets dictionary for further parsing operations """
    @property
    def language(self):
        return self._dict

    @language.setter
    def language(self, value):
        self._dict = value

    """ Gets/Sets linkage limit for LG parser """
    @property
    def linkage_limit(self):
        return self._linkage_limit

    @linkage_limit.setter
    def linkage_limit(self, limit):
        self._linkage_limit = limit

    """ Parses sentense using specified callback function for handling linkages """
    @abstractmethod
    def parse_cbf(self, line, linkagesCallback, param1=None, param2=None):
        pass

    @abstractmethod
    def parse(self, line, callback):
        pass

"""
    LGClientLib handles all Link Grammar operations, using local library
"""
class LGClientLib(LGClient):

    """ Constructor for local LG use """
    def __init__(self, lang, limit = None):
        try:
            self._obj_dict  = Dictionary(lang)
            self._dict      = lang
        except LG_DictionaryError as err:
            print(str(err))

        self._parse_options = ParseOptions(min_null_count=0, max_null_count=999)

        if limit is not None:
            self._parse_options.linkage_limit = limit

    def __del__(self):
        self._parse_options = ParseOptions(verbosity=0)

    """ Property to switch dictionaries between parses """
    @property
    def language(self):
        return self._dict

    @language.setter
    def language(self, value):
        self._dict = None

        if hasattr(self, '_obj_dict') and self._obj_dict is not None:
            del (self._obj_dict)

        try:
            self._obj_dict = Dictionary(value)
            self._dict = value

        except LG_DictionaryError as err:
            print(str(err))

    """ Gets/Sets linkage limit for LG parser """
    @property
    def linkage_limit(self):
        return self._linkage_limit

    @linkage_limit.setter
    def linkage_limit(self, limit):

        if limit is not None:
            self._parse_options.linkage_limit = limit

    """ Parse, using LG API and calls user defined callback function to process linkages """
    def parse_cbf(self, line, linkagesCallback, param1=None, param2=None):

        if hasattr(self, '_obj_dict') and self._obj_dict is not None and \
                hasattr(self, '_parse_options') and self._parse_options is not None:        # need it to avoid AttributeError

            linkages = Sentence(line, self._obj_dict, self._parse_options).parse()

            if linkagesCallback is not None:
                linkagesCallback(linkages, param1, param2)
        else:
            print("Sentence can not be parsed because Dictionary object was not created.")

    def parse(self, line, callback):
        if hasattr(self, '_obj_dict') and self._obj_dict is not None and \
                hasattr(self, '_parse_options') and self._parse_options is not None:        # need it to avoid AttributeError

            linkages = Sentence(line, self._obj_dict, self._parse_options).parse()

            if callback is not None and isinstance(callback, LGClientCallback):
                callback.on_linkages(linkages)
            else:
                print("Error: 'callback' is not an instance of LGClientCallback")

"""
    LGClientREST handles all Link Grammar operations remotely, using REST API service
"""
class LGClientREST(LGClient):

    """ Constructor for use with REST API server """
    def __init__(self, server_url, dict="en", limit=None):

        self._server_url    = server_url
        self._dict          = dict
        self._linkage_limit = limit

    """ Property to switch dictionaries between parses """
    @property
    def language(self):
        return self._dict

    @language.setter
    def language(self, value):
        self._dict = value

    """ Gets/Sets linkage limit for LG parser """
    @property
    def linkage_limit(self):
        return self._linkage_limit

    @linkage_limit.setter
    def linkage_limit(self, limit):
        self._linkage_limit = limit if limit is not None else 1

    def parse_cbf(self, line, linkagesCallback, param1=None, param2=None):

        try:
            # Make up a request string
            req = self._server_url + "?lang=" + self._dict + "&text=" + urllib.parse.quote(line) \
                  + "&mode=1" + "&limit=" + str(self._linkage_limit)

            # Connect to server and run a request
            with urllib.request.urlopen(req) as response:
                html = response.read()

                resp = json.loads(html)

            if linkagesCallback is not None:
                linkagesCallback(resp['linkages'], param1, param2)

        except Exception as err:
            print(err)


    def parse(self, line, callback):

        try:
            # Make up a request string
            req = self._server_url + "?lang=" + self._dict + "&text=" + urllib.parse.quote(line) \
                  + "&mode=1" + "&limit=" + str(self._linkage_limit)

            # Connect to server and run a request
            with urllib.request.urlopen(req) as response:
                html = response.read()

                resp = json.loads(html)

            if callback is not None and isinstance(callback, LGClientCallback):
                callback.on_linkages(resp['linkages'])
            else:
                print("Error: 'callback' is not an instance of LGClientCallback")

        except Exception as err:
            print(err)

def get_lg_client(url):
    if url is None:
        return LGClientLib()
    else:
        return LGClientREST(url)
