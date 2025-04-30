import io
import os
import sys
import traceback
from typing import Any, Optional, Tuple, Union

from pydantic import BaseModel

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.utils import cast_to_output_type
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.code_execution_node_wrappers import ListWrapper, clean_for_dict_wrapper
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


def run_code_inline(
    code: str,
    inputs: EntityInputsInterface,
    output_type: Any,
    filepath: str,
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
                        else clean_for_dict_wrapper(item) if isinstance(item, (dict, list, str)) else item
                    )
                    for item in value
                ]
            )
        return clean_for_dict_wrapper(value)

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
        compiled_code = compile(execution_code, filepath, "exec")
        exec(compiled_code, exec_globals)
    except Exception as e:
        lines = code.splitlines()
        _, _, tb = sys.exc_info()
        tb_generator = traceback.walk_tb(tb)
        stack = traceback.StackSummary.extract(tb_generator)

        # Filter stack to only include frames from the user's code file, and omit the first one
        filtered_stack = traceback.StackSummary.from_list([frame for frame in stack if frame.filename == filepath][1:])
        for frame in filtered_stack:
            if not frame.line and frame.lineno and frame.lineno <= len(lines):
                # Mypy doesn't like us setting private attributes
                frame._line = lines[frame.lineno - 1]  # type: ignore[attr-defined]

        error_message = f"""\
Traceback (most recent call last):
{''.join(filtered_stack.format())}
{e.__class__.__name__}: {e}
"""
        raise NodeException(
            code=WorkflowErrorCode.INVALID_CODE,
            message=error_message,
        )

    logs = log_buffer.getvalue()
    result = exec_globals["__arg__out"]

    result = cast_to_output_type(result, output_type)

    return logs, result
