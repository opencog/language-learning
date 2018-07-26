"""
*   Function callback sample script. Although current version of the library supports both function and class
*       callbacks, it is strongly recommended to use later.
"""

from web.api.lgclient import LGClientError, LGClientLib, LGClientREST


def main():

    def on_rest_linkages(linkages, linkage_callback, param):
        """ Print linkages returned from the server """
        print(linkages)

    def print_diagram(linkage):
        """ Print diagram for a linkage. Called for each linkage returned by local library parser call. """
        print(linkage.diagram())

    def print_postscript(linkage):
        """ Print postscript for a linkage. Called for each linkage returned by local library parser call. """
        print(linkage.postscript())

    def print_constituent(linkage):
        """ Print constituent tree for a linkage. Called for each linkage returned by local library parser call. """
        print(linkage.constituent_tree())

    def print_all(linkage):
        """ Print all three possible outputs for eack linkage. Call for each linkage returned by local library parser call. """
        print_diagram(linkage)
        print_postscript(linkage)
        print_constituent(linkage)

    def on_linkage(linkage, action_callback):
        """ Process a linkage """
        if action_callback is not None:
            action_callback(linkage)

    def on_linkages(linkages, linkage_callback, param):
        """ Process all linkages """
        if linkage_callback is not None:
            for linkage in linkages:
                linkage_callback(linkage, param)

    try:
        client = LGClientLib("en")
        client.parse_cbf("Hello World!", on_linkages, on_linkage, print_diagram)

        client.language = "ru"
        client.parse_cbf("Привет Мир!", on_linkages, on_linkage, print_postscript)

        client.language = "poc-turtle"
        client.parse_cbf("Tuna isa fish.", on_linkages, on_linkage, print_all)

        rest_client = LGClientREST("http://127.0.0.1:9070/linkparser")
        rest_client.linkage_limit = 20
        rest_client.parse_cbf("I'm here, not there.", on_rest_linkages)

        rest_client.language = "ru"
        rest_client.parse_cbf("Привет Мир!", on_rest_linkages)

    except LGClientError as err:
        print(str(err))

    except Exception as err:
        print(str(err))


if __name__ == "__main__":
    main()
