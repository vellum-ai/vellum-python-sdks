import io
import os
import re
from typing import Any, Tuple, Union, get_args, get_origin

from pydantic import BaseModel, ValidationError

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.types.core import EntityInputsInterface


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


def _get_type_name(obj: Any) -> str:
    if isinstance(obj, type):
        return obj.__name__

    if get_origin(obj) is Union:
        children = [_get_type_name(child) for child in get_args(obj)]
        return " | ".join(children)

    return str(obj)


def _cast_to_output_type(result: Any, output_type: Any) -> Any:
    is_valid_output_type = isinstance(output_type, type)
    if get_origin(output_type) is Union:
        allowed_types = get_args(output_type)
        for allowed_type in allowed_types:
            try:
                return _cast_to_output_type(result, allowed_type)
            except NodeException:
                continue
    elif get_origin(output_type) is list:
        allowed_item_type = get_args(output_type)[0]
        if isinstance(result, list):
            return [_cast_to_output_type(item, allowed_item_type) for item in result]
    elif is_valid_output_type and issubclass(output_type, BaseModel) and not isinstance(result, output_type):
        try:
            return output_type.model_validate(result)
        except ValidationError as e:
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message=re.sub(r"\s+For further information visit [^\s]+", "", str(e)),
            ) from e
    elif is_valid_output_type and isinstance(result, output_type):
        return result

    output_type_name = _get_type_name(output_type)
    result_type_name = _get_type_name(type(result))
    raise NodeException(
        code=WorkflowErrorCode.INVALID_OUTPUTS,
        message=f"Expected an output of type '{output_type_name}', but received '{result_type_name}'",
    )


def run_code_inline(
    code: str,
    inputs: EntityInputsInterface,
    output_type: Any,
) -> Tuple[str, Any]:
    log_buffer = io.StringIO()

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
        "print": lambda *args, **kwargs: log_buffer.write(f"{' '.join(args)}\n"),
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

    if output_type != Any:
        result = _cast_to_output_type(result, output_type)

    return logs, result
