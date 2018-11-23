import os
from typing import Dict, List, Any, Union, Callable, NewType

from ..common.absclient import AbstractPipelineComponent
from ..grammar_tester.grammartester import GrammarTesterComponent
from ..grammar_learner import GrammarLearnerComponent
from ..text_parser import TextParserComponent
from ..dash_board.textdashboard import TextFileDashboardComponent
from .varhelper import get_path_from_dict, subst_variables_in_str, subst_variables_in_dict, subst_variables_in_dict2
from .pipelinetreenode import PipelineTreeNode2


__all__ = ['build_tree', 'run_tree']


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

        return {"path": path}


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
            result = handle_request(node, req)

    # Create component instance
    component = get_component(node._component_name, parameters)

    # Execute component
    result = component.run(**{**parameters, **result})

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

    return getattr(inst, meth)(**req)


def prepare_parameters(parent: PipelineTreeNode2, common: dict, specific: dict, environment: dict, first_char="%",
                       create_sub_dir: bool=True) -> (dict, dict):
    """
    Create built-in variables (PREV, RPREV, LEAF, RLEAF), substitute variables, starting with '%'
        with their real values.

    :param parent:          Parent node of the execution tree.
    :param common:          Common parameters dictionary.
    :param specific:        Specific parameters dictionary.
    :param environment:     Environment dictionary.
    :param first_char:      Character that delimits variables ('%' is default).
    :param create_sub_dir   Boolean value forces the program to create subdirectory path based on specific dictionary.
    :return:                Tuple of two dictionaries: one for parameters, another for environment.
    """

    # Merge two dictionaries 'common-parameters' and 'specific-parameters'
    all_parameters = {**common, **specific} if common is not None else specific

    create_leaf = False

    # Check if 'LEAF' path should be created
    for v in all_parameters.values():
        if type(v) == str and v.find("LEAF") >= 0:
            create_leaf = True

    # Path parameters should not appear in other paths
    non_path = {k: v for k, v in zip(specific.keys(), specific.values())
                if (not (isinstance(v, list) or isinstance(v, dict) or isinstance(v, str)))
                or (isinstance(v, str) and v.find("/") < 0 and v.find("%") < 0)}

    # Get subdir path based on specific parameters if requested
    rleaf = get_path_from_dict(non_path, "_") if create_sub_dir else ""

    inherit_prev = all_parameters.get("inherit_prev_path", False)

    leaf = environment["PREV"] + "/" + rleaf if inherit_prev else environment["ROOT"] + "/" + rleaf

    new_environment = {**environment, **{"RLEAF": rleaf, "LEAF": leaf, "CREATE_LEAF": create_leaf}}

    scopes = {"THIS": {**new_environment, **all_parameters}, "PREV": {}} if parent is None else \
             {"THIS": {**new_environment, **all_parameters}, "PREV": {**parent._environment, **parent._parameters}}

    # Substitute derived path for LEAF, PREV and other variables
    all_parameters = subst_variables_in_dict2(all_parameters, scopes, True, first_char)

    # print(all_parameters)

    return all_parameters, new_environment


def build_tree(config: List, globals: dict, first_char="%") -> List[PipelineTreeNode2]:

    parents = list()

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
                            first_char, len(spec) > 1)

                        children.append(PipelineTreeNode2(level, name, parameters, environment, parent))

        else:
            for specific in spec:

                # Create parameter and environment dictionaries
                parameters, environment = prepare_parameters(None, comm, specific, globals, first_char, len(spec) > 1)

                children.append(PipelineTreeNode2(level, name, parameters, environment, None))

        parents = None
        parents = children
        children = None

    return PipelineTreeNode2.roots


def run_tree() -> None:
    PipelineTreeNode2.traverse_all(single_proc_exec)