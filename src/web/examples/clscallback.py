"""
*   Class callback sample. Class callbacks are the preferable way of using the library because you may keep the state
*       of an object within the class instance. Any other functionality may be implemented within the class too.
"""

from linkgrammar import Linkage
from web.lgclient import LGClientCallback, LGClientLib, LGClientREST, LGClientError

"""
    ParseCallback is defined to process link parser's output. Multiple callback classes can be defined when it
        is necessary to handle parsing results differently. 
"""
class ParseCallback(LGClientCallback):

    """ on_linkages is ment to be called whenever the link parser has successfully returned linkages """
    def on_linkages(self, linkages):
        for linkage in linkages:
            self.on_linkage(linkage)

    """ on_linkage is ment to be called for each linkage while processing linkages """
    def on_linkage(self, linkage):
        if type(linkage) == Linkage:
            print(linkage.diagram())

        elif type(linkage) == str:
            print(linkage)
        else:
            print("Error: type missmatch")

    """ on_link is ment to be called for each link when processing links """
    def on_link(self, link):
        pass

def main():
    try:
        # Use the same callback for all languages in this sample
        callback = ParseCallback()

        # Local LG library usage
        client = LGClientLib("en")
        client.parse("Hello World!", callback)

        client.language = "ru"
        client.parse("Привет Мир!", callback)

        # REST API usage sample, Change address and port to appropriate values
        #   if your server settings are different
        rest_client = LGClientREST("http://127.0.0.1:9070/linkparser")
        rest_client.language = "en"

        # Set linkage limit to 20, default is 1
        rest_client.linkage_limit = 20
        rest_client.parse("I'm here, I'm there, I'm everywhere!", callback)

        rest_client.language = "ru"
        rest_client.parse("Привет Вселенная!!!", callback)

    except LGClientError as err:
        print(str(err))

    except Exception as err:
        print(str(err))

if __name__ == "__main__":
    main()