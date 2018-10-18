import os
from typing import Dict, List, Any, Union, Callable, NewType

from ..common.absclient import AbstractPipelineComponent
from ..grammar_tester.grammartester import GrammarTesterComponent, TextFileDashboard
from ..grammar_learner import GrammarLearnerComponent
from ..text_parser import TextParserComponent


__all__ = ['PipelineTreeNode', 'PipelineTreeNode2', 'get_path_from_dict', 'subst_variables_in_str',
           'subst_variables_in_dict', 'build_tree', 'run_tree']


def get_path_from_dict(all: dict) -> str:
    """
    Return path where key/value pairs separated by colon represent a subdirectory.

    :param all:     Dictionary.
    :return:        String path in a form of 'key1:value1/key2:value2/.../key_n:value_n'
    """
    if all is None or len(all) == 0:
        return ""

    return "/".join([item[0].replace("_", "-")+":"+str(item[1]) for item in sorted(all.items(), key=lambda i: i[0])])


def subst_variables_in_str(line: str, values: dict, start_char: str="%") -> object:
    """
    Replace variables inside the specified string

    :param line:        String to replace the variables in.
    :param values:      Dictionary, holding variables and their values.
    :param start_char:  Character used to identify the beginning of a variable inside the string.
    :return:            String where variables have been replaced by their respective values.
    """
    ret_val = line

    for k, v in zip(values.keys(), values.values()):
        ret_val = ret_val.replace(start_char + str(k), str(v))

    return ret_val


def subst_variables_in_dict(var_list: dict, values: dict, start_char: str="%"):
    """
    Substitute variable names with their respected values for each value in the given dictionary

    :param var_list:    Dictionary of parameters to replace variables in.
    :param values:      Dictionary with variable names an their values.
    :return:            New dictionary with
    """
    def subst_value(v:any) -> any:
        return subst_variables_in_str(v, values, start_char) if isinstance(v, str) else v

    return { k:subst_value(v) for k, v in zip(var_list.keys(), var_list.values()) }


class PipelineTreeNode:
    """

    Pipeline execution tree node

    """
    root = None

    def __init__(self,
                 name: str,
                 specific: Dict[str, Any],
                 common: Union[Dict[str, Any], None]=None,
                 environment: Union[Dict[str, Any], None]=None,
                 parent=None):

        if self.root is None:
            self.root = self

        self._component_name: str = name
        self._specific_parameters: Dict[str, Any] = {} if specific is None else specific
        self._common_parameters: Dict[str, Any] = {} if common is None else common
        self._environment: Dict[str, Any] = {} if environment is None else environment
        self._siblings: List[PipelineTreeNode] = []
        self._parent: Union[None, PipelineTreeNode] = parent

    @staticmethod
    def traverse(job: Callable[[Dict, Dict], None], node = None) -> None:
        """

        Traverse pipeline tree executing the job

        :param job:         Function/method to execute for each node.
        :param node:        Node to start from
        :return:            None
        """
        if node is None:
            return None

        job({**node._common_parameters, **node._specific_parameters}, node._environment)

        for sibling in node._siblings:

            PipelineTreeNode.traverse(job, sibling)

    @staticmethod
    def print_node(parameters: dict, environment: dict):
        print(parameters)

    def add_sibling(self, node) -> None:
        """

        Add sibling to pipeline tree

        :param node:    Sibling node to add.
        :return:        None
        """
        self._siblings.append(node)

# ======================================================================================================


class PipelineTreeNode2:
    """

    Pipeline execution tree node

    """
    roots = list()

    def __init__(self,
                 seq_no: int,
                 name: str,
                 parameters: Dict[str, Any],
                 # specific: Dict[str, Any],
                 # common: Union[Dict[str, Any], None]=None,
                 environment: Union[Dict[str, Any], None]=None,
                 parent=None):
        """

        :param seq_no:          Hierarchy level number;
        :param name:            Component name;
        # :param specific:        Specific parameters dictionary;
        # :param common:          Common parameters dictionary;
        :param parameters:      Configuration parameters
        :param environment:     Environment variables dictionary;
        :param parent:          Parent node reference.
        """
        if parent is None:
            self.roots.append(self)

        self.seq_no: int = seq_no
        self._component_name: str = name
        self._parameters: Dict[str, Any] = {} if parameters is None else parameters

        # self._specific_parameters: Dict[str, Any] = {} if specific is None else specific
        # self._common_parameters: Dict[str, Any] = {} if common is None else common

        self._environment: Dict[str, Any] = {} if environment is None else environment
        self._siblings: List[PipelineTreeNode] = []
        self._parent: Union[None, PipelineTreeNode2] = parent

        if self._parent is not None:
            self._parent.add_sibling(self)

    @staticmethod
    def traverse(job: Callable, node = None) -> None:
        """

        Traverse pipeline tree executing the job

        :param job:         Function/method to execute for each node.
        :param node:        Node to start from
        :return:            None
        """
        if node is None:
            return None

        if job is not None:
            job(node)

        # job({**node._common_parameters, **node._specific_parameters}, node._environment)

        for sibling in node._siblings:
            PipelineTreeNode2.traverse(job, sibling)

    @staticmethod
    def traverse_all(job: Callable) -> None:
        """

        Traverse all execution paths of pipeline tree

        :param job:         Function/method to execute for each node.
        :return:            None
        """
        for i, root in enumerate(PipelineTreeNode2.roots, 0):
            print("Execution path: " + str(i))
            PipelineTreeNode2.traverse(job, root)

    @staticmethod
    def print_node(parameters: dict, environment: dict):
        print(parameters)

    def add_sibling(self, node) -> None:
        """

        Add sibling to pipeline tree

        :param node:    Sibling node to add.
        :return:        None
        """
        self._siblings.append(node)


PIPELINE_COMPONENTS = {
    "grammar-tester": GrammarTesterComponent,
    "grammar-learner": GrammarLearnerComponent,
    "text-parser": TextParserComponent,
    # "dash-board": TextFileDashboard
}


def get_component(name: str, params: dict) -> AbstractPipelineComponent:
    """
    Create an instance of the pipeline component

    :param name:    Pipeline component name.
    :return:        AbstractPipelineComponent instance pointer.
    """
    try:
        # Create an instance of specified pipeline component
        component = PIPELINE_COMPONENTS[name](**params)

        # Check the instance to be proper pipeline component
        if not isinstance(component, AbstractPipelineComponent):
            raise Exception("Error: " + str(type(component)) + " is not an instance of AbstractPipelineComponent")

        return component

    except KeyError:
        raise Exception("Error: '{}' is not a valid pipeline component name.".format(name))

    except Exception as err:
        print(str(type(err)) + ": " + str(err))
        raise err


def single_proc_exec(node: PipelineTreeNode2) -> None:

    if node is None:
        return

    leaf = node._environment["LEAF"]
    create = node._environment.get("CREATE_LEAF", False)

    # Create path if it does not exist
    if create and not os.path.isdir(leaf):
        os.makedirs(leaf)

    parameters = node._parameters

    print("\n")
    print("PREV: " + node._environment.get("PREV", "None"))
    print("RPREV: " + node._environment.get("RPREV", "None"))
    print("LEAF: " + node._environment["LEAF"])
    print("RLEAF: " + node._environment["RLEAF"])

    # Create component instance
    # component = get_component(node._component_name, parameters)

    # Execute component
    # component.run(**parameters)

    # Just for debug purposes
    print(node._component_name + ": successfull execution")


def prepare_parameters(common: dict, specific: dict, environment: dict, first_char="%") -> (dict, dict):

    # # Substitute variable names with their respective values
    # specific = subst_variables_in_dict(specific, environment, first_char)

    # Merge two dictionaries 'common-parameters' and 'specific-parameters'
    all_parameters = {**common, **specific} if common is not None else specific
    create_leaf = False

    for v in all_parameters.values():
        if type(v) == str and v.find("LEAF") >= 0:
            create_leaf = True

    # Path parameters should not appear in other paths
    non_path = {k: v for k, v in zip(specific.keys(), specific.values()) if not isinstance(v, str)
                or (isinstance(v, str) and v.find("/") < 0)}

    # Get subdir path based on specific parameters
    rleaf = get_path_from_dict(non_path)
    leaf = environment["ROOT"] + "/" + rleaf
    new_environment = {**environment, **{"RLEAF": rleaf, "LEAF": leaf, "CREATE_LEAF": create_leaf}}

    # Substitute derived path for LEAF, PREV and other variables
    all_parameters = subst_variables_in_dict(all_parameters, new_environment, first_char)

    return all_parameters, new_environment


def build_tree(config: List, globals: dict, first_char="%") -> List[PipelineTreeNode2]:

    parents = list()

    for level, component_config in enumerate(config):

        name = component_config["component"]
        comm = component_config["common-parameters"]
        spec = component_config["specific-parameters"]

        children = list()

        if len(parents):
            for parent in parents:

                if parent._parameters.get("follow_exec_path", True):
                    for specific in spec:

                        parameters, environment = prepare_parameters(
                            comm, specific,
                            {**globals, **{"RPREV": parent._environment["RLEAF"], "PREV": parent._environment["LEAF"]}},
                            first_char)

                        children.append(PipelineTreeNode2(level, name, parameters, environment, parent))

        else:
            for specific in spec:
                parameters, environment = prepare_parameters(comm, specific, globals, first_char)

                children.append(PipelineTreeNode2(level, name, parameters, environment, None))

        parents = None
        parents = children
        children = None

    return PipelineTreeNode2.roots

def run_tree() -> None:
    PipelineTreeNode2.traverse_all(single_proc_exec)