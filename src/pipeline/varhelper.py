from typing import Dict, Union, Type, Any

__all__ = ['get_path_from_dict', 'subst_variables_in_str', 'subst_variables_in_dict', 'subst_variables_in_dict2']


def get_path_from_dict(params: dict, delimiter: str = "_") -> str:
    """
    Return path where key/value pairs separated by colon represent a subdirectory.

    :param params:     Dictionary.
    :param delimiter   Character that delimits key/value pairs.
    :return:           String path in a form of 'key1:value1/key2:value2/.../key_n:value_n'
    """
    if params is None or len(params) == 0:
        return ""

    return delimiter.join([item[0].replace("_", "-") + ":"+str(item[1])
                           for item in sorted(params.items(), key=lambda i: i[0])])


def subst_variables_in_str(line: str, values: dict, start_char: str = "%") -> object:
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


def get_variable_value(line, values: Dict[str, object]) -> (Union[str, None], Union[object, None], Type):
    """
    Find longest key match and return it respective value and type

    :param line:        Line to search in.
    :param values:      Dictionary with scope variables and their respective values.
    :return:            Tuple (key, value) corresponding the longest variable match.
    """
    line_len = len(line)

    sorted_keys = sorted(values.keys(), key=len, reverse=True)

    for key in sorted_keys:

        key_len = len(key)

        if key_len > line_len:
            continue

        if line[0:key_len] == key:
            return key, values[key], type(values[key])

    return None, None, None


def get_referenced_variable_value(line: str, scopes: Dict[str, Dict[str, object]]):
    # -> Union[(str, str), (None, None)]:
    """
    Return value corresponding to referenced variable name

    :param line:        Line to search in.
    :param scopes:      Scope dictionaries to get variable values from.
    :return:            Tuple (key, value) referenced variable name and its respective value.
    """
    line_len = len(line)

    # Check if that's a scope
    key, values, cls = get_variable_value(line, scopes)

    # If the scope is not explicitly set
    if key is None:

        # Search the current scope
        key, value, cls = get_variable_value(line, scopes["THIS"])

        if key is not None:
            return key, value, cls

        # Raise exception if not found in current scope
        raise NameError("Variable '{}' is unknown within the scope.".format(line))

    key_len = len(key)

    # Name of the scope without variable name is treated as 'LEAF'
    if line_len == key_len or (line_len > key_len and line[key_len] != "."):
        return key, values["LEAF"], type(values["LEAF"])

    scope = key

    # Get value for variable name
    key, value, cls = get_variable_value(line[key_len+1:], values)

    if key is None:
        raise NameError("Variable '{}' is unknown within the scope '{}'.".format(line[key_len + 1:], scope))

    return scope + "." + key, value, cls


def subst_all_vars_in_str(line: str, scopes: dict, start_char: str = "%") -> Any:
    """
    Replace all variables with their respective values

    :param line:        String to replace variables in.
    :param scopes:      Dictionary with two or more scopes.
    :param start_char:  Symbol to delimit a variable.
    :return:            String with replaced variables.
    """
    new_line = line
    num_repl = 0
    key, val, cls = None, None, None

    while True:
        pos = new_line.find(start_char)

        if pos < 0:
            break

        key, val, cls = get_referenced_variable_value(new_line[pos+1:], scopes)

        new_line = new_line.replace(start_char + key, str(val), 1)

        num_repl += 1

    # If the string consists of nothing but only one variable reference and its type is other than string,
    if num_repl == 1 and cls.__name__ != "str" and len(line) == len(key) + 1:

        # Convert to referenced variable value type on return.
        return cls(new_line)

    return new_line


def subst_variables_in_dict2(var_list: dict, scopes: dict, is_nested: bool = True, start_char: str = "%") -> dict:
    """
    Substitute variable names with their respected values for each value in the given dictionary

    :param var_list:    Dictionary of parameters to replace variables in.
    :param scopes:      Dictionary with variable names an their values.
    :param is_nested:   If True replaces variables in string variables in nested dictionaries and lists.
    :param start_char:  Character that delimits variables in strings.
    :return:            New dictionary with
    """
    def subst_value(v: any) -> any:
        if isinstance(v, str):
            return subst_all_vars_in_str(v, scopes, start_char)
        elif isinstance(v, dict) and is_nested:
            return subst_variables_in_dict2(v, scopes, is_nested, start_char)
        elif isinstance(v, list) and is_nested:
            return [subst_value(val) for val in v]
        else:
            return v

    return {k: subst_value(v) for k, v in zip(var_list.keys(), var_list.values())}


def subst_variables_in_dict(var_list: dict, values: dict, start_char: str = "%"):
    """
    Substitute variable names with their respected values for each value in the given dictionary

    :param var_list:    Dictionary of parameters to replace variables in.
    :param values:      Dictionary with variable names an their values.
    :param start_char:  Character that delimits variables in strings.
    :return:            New dictionary with
    """
    def subst_value(v: any) -> any:
        return subst_variables_in_str(v, values, start_char) if isinstance(v, str) else v

    return {k: subst_value(v) for k, v in zip(var_list.keys(), var_list.values())}
