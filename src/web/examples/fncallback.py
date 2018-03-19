"""
*   Function callback sample script. Although current version of the library supports both function and class
*       callbacks, it is strongly recommended to use later.
"""

from web.lgclient import LGClientError, LGClientLib, LGClientREST


def main():

    """ Print linkages returned from the server """
    def onRestLinkages(linkages, linkageCallback, param):
        print(linkages)

    """ Print diagram for a linkage. Called for each linkage returned by local library parser call. """
    def printDiagram(linkage):
        print(linkage.diagram())

    """ Print postscript for a linkage. Called for each linkage returned by local library parser call. """
    def printPostscript(linkage):
        print(linkage.postscript())

    """ Print constituent tree for a linkage. Called for each linkage returned by local library parser call. """
    def printConstituent(linkage):
        print(linkage.constituent_tree())

    """ Print all three possible outputs for eack linkage. Call for each linkage returned by local library parser call. """
    def printAll(linkage):
        printDiagram(linkage)
        printPostscript(linkage)
        printConstituent(linkage)

    """ Process a linkage """
    def onLinkage(linkage, actionCallback):
        if actionCallback is not None:
            actionCallback(linkage)

    """ Process all linkages """
    def onLinkages(linkages, linkageCallback, param):
        if linkageCallback is not None:
            for linkage in linkages:
                linkageCallback(linkage, param)

    try:
        client = LGClientLib("en")
        client.parse_cbf("Hello World!", onLinkages, onLinkage, printDiagram)

        client.language = "ru"
        client.parse_cbf("Привет Мир!", onLinkages, onLinkage, printPostscript)

        client.language = "poc-turtle"
        client.parse_cbf("Tuna isa fish.", onLinkages, onLinkage, printAll)

        rest_client = LGClientREST("http://127.0.0.1:9070/linkparser")
        rest_client.linkage_limit = 20
        rest_client.parse_cbf("I'm here, not there.", onRestLinkages)

        rest_client.language = "ru"
        rest_client.parse_cbf("Привет Мир!", onRestLinkages)

    except LGClientError as err:
        print(str(err))

    except Exception as err:
        print(str(err))

if __name__ == "__main__":
    main()