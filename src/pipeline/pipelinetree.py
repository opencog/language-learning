import os
from typing import Dict, List, Any, Union, Callable, NewType

from ..common.absclient import AbstractPipelineComponent
from ..grammar_tester.grammartester import GrammarTesterComponent
from ..grammar_learner import GrammarLearnerComponent
from ..text_parser import TextParserComponent
from ..dash_board.textdashboard import TextFileDashboardComponent
from .varhelper import get_path_from_dict, subst_variables_in_str, subst_variables_in_dict, subst_variables_in_dict2

__all__ = ['PipelineTreeNode2', 'build_tree', 'run_tree']


class PathCreatorComponent(AbstractPipelineComponent):
    def __init__(self):
        pass

    def validate_parameters(self, **kwargs):
        return True

    def run(self, **kwargs):
        return {}

    @staticmethod
    def create(**kwargs):
        path = kwargs.get("path", None)

        if path is not None and not os.path.isdir(path):
            os.makedirs(path)


class PipelineTreeNode2:
    """

    Pipeline execution tree node

    """
    roots = list()
    static_components = dict()

    def __init__(self,
                 seq_no: int,
                 name: str,
                 parameters: Dict[str, Any],
                 environment: Union[Dict[str, Any], None]=None,
                 parent=None):
        """

        :param seq_no:          Hierarchy level number;
        :param name:            Component name;
        :param parameters:      Configuration parameters
        :param environment:     Environment variables dictionary;
        :param parent:          Parent node reference.
        """
        if parent is None:
            self.roots.append(self)

        self.seq_no: int = seq_no
        self._component_name: str = name
        self._parameters: Dict[str, Any] = {} if parameters is None else parameters
        self._environment: Dict[str, Any] = {} if environment is None else environment
        self._siblings: List[PipelineTreeNode2] = []
        self._parent: Union[None, PipelineTreeNode2] = parent

        if self._parent is not None:
            self._parent.add_sibling(self)

    @staticmethod
    def free_static_components():
        for o in PipelineTreeNode2.static_components.values():
            if o is not None:
                del o

        PipelineTreeNode2.static_components = dict()

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
            try:
                job(node)
            except Exception as err:
                print("Error: " + str(err))
                return None

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
    "path-creator": PathCreatorComponent,
    "grammar-tester": GrammarTesterComponent,
    "grammar-learner": GrammarLearnerComponent,
    "text-parser": TextParserComponent,
    "dash-board": TextFileDashboardComponent
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
    result = {}

    pre_exec = parameters.get("pre-exec-req", None)

    if pre_exec:
        for req in pre_exec:
            handle_request(node, req)

    # Create component instance
    component = get_component(node._component_name, parameters)

    # Execute component
    result = component.run(**parameters)

    post_exec = parameters.get("post-exec-req", None)

    if post_exec:
        for req in post_exec:
            handle_request(node, {**req, **result})

    # Just for debug purposes
    print(node._component_name + ": successfull execution")


def handle_request(node: PipelineTreeNode2, req: dict) -> None:
    """
    Handle Post-execute Request

    :param node:        Pipiline tree node reference.
    :param req:         Request parameter dictionary.
    :return:            None
    """
    obj = req.pop("obj", None)

    if obj is None:
        raise Exception("Error: Mandatory parameter 'obj' does not exist.")

    pos = str(obj).find(".")

    if pos < 0:
        raise Exception("Error: Object name and method should be separated by comma.")

    name = obj[:pos]
    meth = obj[pos+1:]

    inst = node.static_components.get(name, None)

    if inst is None:
        raise Exception("Error: static component '{}' does not exist.".format(name))

    getattr(inst, meth)(**req)


# def prepare_parameters(common: dict, specific: dict, environment: dict, first_char="%") -> (dict, dict):
#
#     # # Substitute variable names with their respective values
#     # specific = subst_variables_in_dict(specific, environment, first_char)
#
#     # Merge two dictionaries 'common-parameters' and 'specific-parameters'
#     all_parameters = {**common, **specific} if common is not None else specific
#     create_leaf = False
#
#     # Check if 'LEAF' path should be created
#     for v in all_parameters.values():
#         if type(v) == str and v.find("LEAF") >= 0:
#             create_leaf = True
#
#     # Path parameters should not appear in other paths
#     non_path = {k: v for k, v in zip(specific.keys(), specific.values()) if not isinstance(v, str)
#                 or (isinstance(v, str) and v.find("/") < 0)}
#
#     # Get subdir path based on specific parameters
#     rleaf = get_path_from_dict(non_path)
#
#     inherit_prev = all_parameters.get("inherit_prev_path", False)
#
#     leaf = environment["PREV"] + "/" + rleaf if inherit_prev else environment["ROOT"] + "/" + rleaf
#
#     new_environment = {**environment, **{"RLEAF": rleaf, "LEAF": leaf, "CREATE_LEAF": create_leaf}}
#
#     # Substitute derived path for LEAF, PREV and other variables
#     all_parameters = subst_variables_in_dict(all_parameters, new_environment, first_char)
#
#     return all_parameters, new_environment


def prepare_parameters(parent: PipelineTreeNode2, common: dict, specific: dict, environment: dict, first_char="%") -> (dict, dict):

    # # Substitute variable names with their respective values
    # specific = subst_variables_in_dict(specific, environment, first_char)

    # Merge two dictionaries 'common-parameters' and 'specific-parameters'
    all_parameters = {**common, **specific} if common is not None else specific
    create_leaf = False

    # Check if 'LEAF' path should be created
    for v in all_parameters.values():
        if type(v) == str and v.find("LEAF") >= 0:
            create_leaf = True

    # Path parameters should not appear in other paths
    non_path = {k: v for k, v in zip(specific.keys(), specific.values()) if not isinstance(v, str)
                or (isinstance(v, str) and v.find("/") < 0)}

    # Get subdir path based on specific parameters
    rleaf = get_path_from_dict(non_path)

    inherit_prev = all_parameters.get("inherit_prev_path", False)

    leaf = environment["PREV"] + "/" + rleaf if inherit_prev else environment["ROOT"] + "/" + rleaf

    new_environment = {**environment, **{"RLEAF": rleaf, "LEAF": leaf, "CREATE_LEAF": create_leaf}}

    scopes = {"THIS": {**new_environment, **all_parameters}, "PREV": {}} if parent is None else \
             {"THIS": {**new_environment, **all_parameters}, "PREV": {**parent._environment, **parent._parameters}}

    # scopes = {"THIS": new_environment, "PREV": {}} if parent is None else \
    #     {"THIS": new_environment, "PREV": {**parent._environment, **parent._parameters}}

    # Substitute derived path for LEAF, PREV and other variables
    all_parameters = subst_variables_in_dict2(all_parameters, scopes, True, first_char)

    print(all_parameters)

    return all_parameters, new_environment


def build_tree(config: List, globals: dict, first_char="%") -> List[PipelineTreeNode2]:

    parents = list()

    # print(config)

    for level, component_config in enumerate(config):

        name = component_config.get("component", None)
        type = component_config.get("type", "dynamic")
        comm = component_config.get("common-parameters", None)
        spec = component_config.get("specific-parameters", None)

        if name is None:
            raise Exception("No 'component' parameter found in configuration.")

        if type == "dynamic" and spec is None:
            raise Exception("No 'specific-parameters' section found in configuration.")

        if type == "static":
            params = subst_variables_in_dict(component_config.get("parameters", {}), globals, first_char)

            print(params)

            inst_name = component_config.get("instance-name", None)

            if inst_name is not None:
                PipelineTreeNode2.static_components[inst_name] = get_component(name, params)

            continue

        children = list()

        if len(parents):
            for parent in parents:

                # Only if the previous component path should be followed
                if parent._parameters.get("follow_exec_path", True):
                    for specific in spec:

                        # Create parameter and environment dictionaries
                        parameters, environment = prepare_parameters(
                            parent, comm, specific,
                            {**globals, **{"RPREV": parent._environment["RLEAF"], "PREV": parent._environment["LEAF"]}},
                            first_char)

                        children.append(PipelineTreeNode2(level, name, parameters, environment, parent))

        else:
            for specific in spec:

                # Create parameter and environment dictionaries
                parameters, environment = prepare_parameters(None, comm, specific, globals, first_char)

                children.append(PipelineTreeNode2(level, name, parameters, environment, None))

        parents = None
        parents = children
        children = None

    return PipelineTreeNode2.roots

# def build_tree(config: List, globals: dict, first_char="%") -> List[PipelineTreeNode2]:
#
#     parents = list()
#
#     # print(config)
#
#     for level, component_config in enumerate(config):
#
#         name = component_config.get("component", None)
#         type = component_config.get("type", "dynamic")
#         comm = component_config.get("common-parameters", None)
#         spec = component_config.get("specific-parameters", None)
#
#         if name is None:
#             raise Exception("No 'component' parameter found in configuration.")
#
#         if type == "dynamic" and spec is None:
#             raise Exception("No 'specific-parameters' section found in configuration.")
#
#         if type == "static":
#             params = subst_variables_in_dict(component_config.get("parameters", {}), globals, first_char)
#
#             PipelineTreeNode2.static_components[name] = get_component(name, params)
#             continue
#
#         children = list()
#
#         if len(parents):
#             for parent in parents:
#
#                 # Only if the previous component path should be followed
#                 if parent._parameters.get("follow_exec_path", True):
#                     for specific in spec:
#
#                         # Create parameter and environment dictionaries
#                         parameters, environment = prepare_parameters(
#                             comm, specific,
#                             {**globals, **{"RPREV": parent._environment["RLEAF"], "PREV": parent._environment["LEAF"]}},
#                             first_char)
#
#                         children.append(PipelineTreeNode2(level, name, parameters, environment, parent))
#
#         else:
#             for specific in spec:
#
#                 # Create parameter and environment dictionaries
#                 parameters, environment = prepare_parameters(comm, specific, globals, first_char)
#
#                 children.append(PipelineTreeNode2(level, name, parameters, environment, None))
#
#         parents = None
#         parents = children
#         children = None
#
#     return PipelineTreeNode2.roots


def run_tree() -> None:
    PipelineTreeNode2.traverse_all(single_proc_exec)