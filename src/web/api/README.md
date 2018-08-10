# Simple Link Grammar REST API implementation
This part of the repository contains server side and client side Link Grammar REST API implementaiton.
Server script uses Falcon library to handle all HTTP interactions. It was tested only with Gunicorn WSGI server, 
but should be working with any WSGI server. All scripts were written for Python 3 and never tested with Python 2,
so be precausioned. Client side library hides Link Grammar parser implementation from a user.
It can be used with both localy installed Python library and remote REST API Web service. Usage samples can be found 
in Examples subfolder. 

## Web Service Installation
Before running the script make sure linkgrammar, falcon and gunicorn packages are installed in Python virtual 
environment you will be running your web service in. Then you may start the script typing:

    gunicorn -b 127.0.0.1:9070 lgrestparser:api

The service will be available at `http://127.0.0.1:9070/linkparser`. Use your own address and port when starting 
the script.

## Web Service Usage
In current version the service responds to HTTP GET requests only. It accepts four arguments. One of them `text` is 
mandatory, the others are optional. Here is the sample request string:

    http://127.0.0.1:9070/linkparser?text=Hello%20World!&lang=en&mode=0&limit=10

where:
* `text` - sentence to parse
* `lang` - language, can be any language supported by Link Grammar
* `mode` - output mode, can be 0-diagram; 1-postscript; 2-constituent tree; 3-ULL sentence
* `limit`- maximum number of linkages that can be returned

## Client Library 
The client library can be used either with Web service or with locally installed Link Grammar library exactly the
same way. It uses callbacks to process parsing results. There are two types of callbacks in current version of the
library: function callback and class callback. Although class callback is the prefered way, any type can be used.
See examples for more detailed info. 