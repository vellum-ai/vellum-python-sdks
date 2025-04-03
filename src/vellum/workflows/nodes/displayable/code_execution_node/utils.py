import io
import os
from typing import Any, Optional, Tuple, Union

from pydantic import BaseModel

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.utils import cast_to_output_type
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.core import EntityInputsInterface


def read_file_from_path(
    node_filepath: str, script_filepath: str, context: Optional[WorkflowContext] = None
) -> Union[str, None]:
    node_filepath_dir = os.path.dirname(node_filepath)
    full_filepath = os.path.join(node_filepath_dir, script_filepath)

    # If dynamic file loader is present, try and read the code from there
    if context and context.generated_files:
        # Strip out namespace
        normalized_path = os.path.normpath(full_filepath)
        stripped_node_filepath = "/".join(normalized_path.split("/")[1:])

        code = context.generated_files.get(stripped_node_filepath, None)
        if code is not None:
            return code

    # Default logic for reading from filesystem
    try:
        with open(full_filepath) as file:
            return file.read()
    except (FileNotFoundError, IsADirectoryError):
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
            if attr == "value":
                # In order to be backwards compatible with legacy Workflows, which wrapped
                # several values as VellumValue objects, we use the "value" key to return itself
                return self

            raise AttributeError(f"dict has no key: '{attr}'")

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
    inputs: EntityInputsInterface,
    output_type: Any,
) -> Tuple[str, Any]:
    log_buffer = io.StringIO()

    def _inline_print(*args: Any, **kwargs: Any) -> None:
        str_args = [str(arg) for arg in args]
        print_line = f"{' '.join(str_args)}\n"
        log_buffer.write(print_line)

    def wrap_value(value):
        if isinstance(value, list):
            return ListWrapper(
                [
                    # Convert VellumValue to dict with its fields
                    (
                        item.model_dump()
                        if isinstance(item, BaseModel)
                        else _clean_for_dict_wrapper(item) if isinstance(item, (dict, list)) else item
                    )
                    for item in value
                ]
            )
        return _clean_for_dict_wrapper(value)

    exec_globals = {
        "__arg__inputs": {name: wrap_value(value) for name, value in inputs.items()},
        "__arg__out": None,
        "print": _inline_print,
    }
    run_args = [f"{name}=__arg__inputs['{name}']" for name in inputs.keys()]
    execution_code = f"""\
{code}

__arg__out = main({", ".join(run_args)})
"""
    try:
        exec(execution_code, exec_globals)
    except Exception as e:
        raise NodeException(
            code=WorkflowErrorCode.INVALID_CODE,
            message=str(e),
        )

    logs = log_buffer.getvalue()
    result = exec_globals["__arg__out"]

    result = cast_to_output_type(result, output_type)

    return logs, result
