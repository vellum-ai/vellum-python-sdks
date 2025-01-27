from contextlib import redirect_stdout
import io
import os
from typing import Any, List, Tuple, Union

from vellum.client.types.code_executor_input import CodeExecutorInput
from vellum.workflows.nodes.utils import parse_type_from_str


def read_file_from_path(node_filepath: str, script_filepath: str) -> Union[str, None]:
    node_filepath_dir = os.path.dirname(node_filepath)
    full_filepath = os.path.join(node_filepath_dir, script_filepath)

    if os.path.isfile(full_filepath):
        with open(full_filepath) as file:
            return file.read()
    return None


class ListWrapper(list):
    def __getitem__(self, key):
        item = super().__getitem__(key)
        if not isinstance(item, DictWrapper) and not isinstance(item, ListWrapper):
            self.__setitem__(key, _clean_for_dict_wrapper(item))

        return super().__getitem__(key)


class DictWrapper(dict):
    """
    This wraps a dict object to make it behave basically the same as a standard javascript object
    and enables us to use vellum types here without a shared library since we don't actually
    typecheck things here.
    """

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, attr):
        if attr not in self:
            raise AttributeError(f"Vellum object has no attribute '{attr}'")

        item = super().__getitem__(attr)
        if not isinstance(item, DictWrapper) and not isinstance(item, ListWrapper):
            self.__setattr__(attr, _clean_for_dict_wrapper(item))

        return super().__getitem__(attr)

    def __setattr__(self, name, value):
        self[name] = value


def _clean_for_dict_wrapper(obj):
    if isinstance(obj, dict):
        wrapped = DictWrapper(obj)
        for key in wrapped:
            wrapped[key] = _clean_for_dict_wrapper(wrapped[key])

        return wrapped

    elif isinstance(obj, list):
        return ListWrapper(map(lambda item: _clean_for_dict_wrapper(item), obj))

    return obj


def run_code_inline(
    code: str,
    input_values: List[CodeExecutorInput],
    output_type: Any,
) -> Tuple[str, Any]:
    log_buffer = io.StringIO()
    delimiter = "--vellum-output-start--"
    max_output_length = "16_000_000"

    run_args = [f"{input_value.name}={input_value.name}" for input_value in input_values]
    execution_code = f"""\
{code}

import json

out = json.dumps(main({", ".join(run_args)})).strip().splitlines()[-1][:{max_output_length}]
print("{delimiter}")
print(out)"""
    local_namespace = {input_value.name: _clean_for_dict_wrapper(input_value.value) for input_value in input_values}

    with redirect_stdout(log_buffer):
        exec(execution_code, local_namespace)

    logs = log_buffer.getvalue()
    output_lines = logs.split(delimiter)
    execution_logs = output_lines[0]
    result_as_str = output_lines[1] if len(output_lines) > 1 else ""
    result = parse_type_from_str(result_as_str, output_type)
    return execution_logs, result
