#!/usr/bin/env python3

"""

    This library is intended to simpify the use of localy installed Link Grammar API and Link Grammar REST API.
    Class wrapper allows to use both with the same set of methods and handle parsing results the same way.

"""

from linkgrammar import LG_DictionaryError, Sentence, ParseOptions, Dictionary
from abc import ABCMeta, abstractmethod
import urllib.request
import urllib.parse
import json

__all__     = [
                'LGClientError', 'LGClient', 'LGClientCallback', 'LGClientLib', 'LGClientREST', 'LGClientCallback',
                'get_lg_client'
              ]

__version__ = '0.1'


class LGClientError(Exception):
    """
        Exception class for all Link Grammar clients

    """

    def __init__(self, err_msg, err_code=1):
        self._err_msg = err_msg
        self._err_code = err_code

    def __str__(self):
        return self._err_msg


class LGClientCallback(metaclass=ABCMeta):
    """
        Abstract class defines callback interface
    """

    @abstractmethod
    def on_linkages(self, linkages):
        """ Linkages processig callback method """
        pass

    @abstractmethod
    def on_linkage(self, linkage):
        """ Linkage processig callback method """
        pass

    @abstractmethod
    def on_link(self, link):
        """ Link processig callback method """
        pass


class LGClient(metaclass=ABCMeta):
    """
        Base class for all Link Grammar clients
    """
    def __init__(self):
        self._dict = "en"
        self._linkage_limit = 10000

    @property
    def language(self):
        """ Get/set dictionary for further parsing operations """
        return self._dict

    @language.setter
    def language(self, value):
        self._dict = value

    @property
    def linkage_limit(self):
        """ Get/set linkage limit for LG parser """
        return self._linkage_limit

    @linkage_limit.setter
    def linkage_limit(self, limit):
        self._linkage_limit = limit

    @abstractmethod
    def parse_cbf(self, line, callback, param1=None, param2=None):
        """ Parse sentense using specified callback function for processing linkages """
        pass

    @abstractmethod
    def parse(self, line, callback):
        """ Parse sentense using specified class callback instance for processing linkages """
        pass


class LGClientLib(LGClient):
    """
        LGClientLib handles all Link Grammar operations, using local library
    """

    def __init__(self, lang, limit=None):
        """ Constructor for local LG use """
        super().__init__()

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

    @property
    def language(self):
        """ Property to switch dictionaries between parses """
        return self._dict

    @language.setter
    def language(self, value):
        self._dict = None

        if hasattr(self, '_obj_dict') and self._obj_dict is not None:
            del self._obj_dict

        try:
            self._obj_dict = Dictionary(value)
            self._dict = value

        except LG_DictionaryError as err:
            print(str(err))

    @property
    def linkage_limit(self):
        """ Get/set linkage limit for LG parser """
        return self._linkage_limit

    @linkage_limit.setter
    def linkage_limit(self, limit):

        if limit is not None:
            self._parse_options.linkage_limit = limit

    def parse_cbf(self, line, callback, param1=None, param2=None):
        """ Parse sentence, using user defined callback function for processing linkages """

        if hasattr(self, '_obj_dict') and self._obj_dict is not None and \
                hasattr(self, '_parse_options') and self._parse_options is not None:

            linkages = Sentence(line, self._obj_dict, self._parse_options).parse()

            if callback is not None:
                callback(linkages, param1, param2)
        else:
            raise LGClientError("Sentence can not be parsed because Dictionary object was not created.")

    def parse(self, line, callback):
        """
            Parse sentence, using user defined callback class
            for processing linkages
        """
        if hasattr(self, '_obj_dict') and self._obj_dict is not None and \
                hasattr(self, '_parse_options') and self._parse_options is not None:

            linkages = Sentence(line, self._obj_dict, self._parse_options).parse()

            if callback is not None and isinstance(callback, LGClientCallback):
                callback.on_linkages(linkages)
            else:
                raise LGClientError("Error: 'callback' is not an instance of LGClientCallback")


class LGClientREST(LGClient):
    """
        LGClientREST handles all Link Grammar operations remotely, using REST API service
    """

    def __init__(self, server_url, dict="en", limit=None):
        """ Constructor for use with REST API server """

        super().__init__()
        self._server_url    = server_url
        self._dict          = dict
        self._linkage_limit = limit

    @property
    def language(self):
        """ Property to switch dictionaries between parses """
        return self._dict

    @language.setter
    def language(self, value):
        self._dict = value

    @property
    def linkage_limit(self):
        """ Get/set linkage limit for LG parser """
        return self._linkage_limit

    @linkage_limit.setter
    def linkage_limit(self, limit):
        self._linkage_limit = limit if limit is not None else 1

    def parse_cbf(self, line, callback, param1=None, param2=None):
        """
            Parse sentence using callback function for result processing
        """
        if callback is None:
            raise LGClientError("Error: Callback function argument has type 'None'.")

        try:
            # Make up a request string
            req = self._server_url + "?lang=" + self._dict + "&text=" + urllib.parse.quote(line) \
                  + "&mode=1" + "&limit=" + str(self._linkage_limit)

            # Connect to server and run a request
            with urllib.request.urlopen(req) as response:
                html = response.read()

                resp = json.loads(html)

            callback(resp['linkages'], param1, param2)

        except Exception as err:
            print(err)

    def parse(self, line, callback):
        """
            Parse sentence using class callback instance for result processig
        """

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
                raise LGClientError("Error: 'callback' is not an instance of LGClientCallback")

        except Exception as err:
            print(err)


def get_lg_client(lang, url=None):
    """
        get_lg_client is the universal method of creating LGClient instance. Local library is used if server URL
                is not set, REST API client is used otherwise.
    """
    if lang is None:
        raise LGClientError("Error: 'lang' argument is not properly set.")

    if url is None:
        return LGClientLib(lang)
    else:
        return LGClientREST(lang, url)
