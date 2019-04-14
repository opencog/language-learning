from ..common.absclient import AbstractDashboardClient, DashboardError, AbstractStatEventHandler
from ..common.parsemetrics import ParseMetrics, ParseQuality
from ..common.absclient import AbstractConfigClient
from ..dash_board.textdashboard import TextFileDashboard, CONF_ROW_KEY, CONF_COL_KEY, CONF_ROW_IND, \
    CONF_COL_IND, CONF_VAL_KEYS


__all__ = ["TextFileDashboardConf"]     # , "HTMLFileDashboard"]


class TextFileDashboardConf(TextFileDashboard, AbstractStatEventHandler):
    """
    Class which implements text file serialization.
        Exceptions: IndexError, ValueError
    """
    def __init__(self, cfg_man: AbstractConfigClient):

        if not isinstance(cfg_man, AbstractConfigClient):
            raise Exception("'cfg_man' should be an instance of AbstractConfigClient base class")

        self._config = cfg_man.get_config("", "dash-board")[0]

        super().__init__(self._config)

    def on_statistics(self, nodes: list, metrics: ParseMetrics, quality: ParseQuality):

        # Return if dashboard is not configured.
        if self._config is None:
            return

        # row_key, col_key = None, None
        row_ind, col_ind = None, None

        try:
            # Get row and column keys
            row_key = self._config[CONF_ROW_KEY].format(*nodes)
            col_key = self._config[CONF_COL_KEY].format(*nodes)

            # Get row and column indexes
            row_ind = self._config[CONF_ROW_IND][row_key]
            col_ind = self._config[CONF_COL_IND][col_key]

        except IndexError as err:
            print("on_statatistics(): IndexError: " + str(err))
            return

        except KeyError as err:
            print("on_statatistics(): KeyError: " + str(err))
            return

        for row in row_ind:
            for col in col_ind:

                val_str = None

                try:
                    # Get value key string by column index
                    val_str = self._config[CONF_VAL_KEYS][col].format(nodes=nodes,
                                                                      parseability=metrics.parseability_str(metrics),
                                                                      parsequality=quality.parse_quality_str(quality),
                                                                      F1=quality.f1_str(quality),
                                                                      parsetime=metrics.parse_time_str(metrics))

                except IndexError as err:
                    print("on_statatistics():2: IndexError: " + str(err))
                    continue

                except KeyError as err:
                    print("on_statatistics():2: KeyError: " + str(err))
                    continue

                # Put value into the table
                self.set_cell_by_indexes(row, col, val_str)
