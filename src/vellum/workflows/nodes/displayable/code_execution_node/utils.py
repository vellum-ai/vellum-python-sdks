import io
import os
import re
from typing import Any, List, Tuple, Union

from pydantic import BaseModel, ValidationError

from vellum.client.types.code_executor_input import CodeExecutorInput
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException


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

    exec_globals = {
        "__arg__inputs": {input_value.name: _clean_for_dict_wrapper(input_value.value) for input_value in input_values},
        "__arg__out": None,
        "print": lambda *args, **kwargs: log_buffer.write(f"{' '.join(args)}\n"),
    }
    run_args = [f"{input_value.name}=__arg__inputs['{input_value.name}']" for input_value in input_values]
    execution_code = f"""\
{code}

__arg__out = main({", ".join(run_args)})
"""

    exec(execution_code, exec_globals)

    logs = log_buffer.getvalue()
    result = exec_globals["__arg__out"]

    if issubclass(output_type, BaseModel) and not isinstance(result, output_type):
        try:
            result = output_type.model_validate(result)
        except ValidationError as e:
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message=re.sub(r"\s+For further information visit [^\s]+", "", str(e)),
            ) from e

    if not isinstance(result, output_type):
        raise NodeException(
            code=WorkflowErrorCode.INVALID_OUTPUTS,
            message=f"Expected an output of type '{output_type.__name__}', but received '{result.__class__.__name__}'",
        )

    return logs, result
