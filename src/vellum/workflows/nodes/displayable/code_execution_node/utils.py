import io
import os
import sys
import traceback
from typing import Any, Optional, Tuple, Union

from vellum import Vellum
from vellum.workflows.constants import undefined
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.utils import cast_to_output_type, wrap_inputs_for_backward_compatibility
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


def run_code_inline(
    code: str,
    inputs: EntityInputsInterface,
    output_type: Any,
    filepath: str,
    vellum_client: Vellum,
) -> Tuple[str, Any]:
    log_buffer = io.StringIO()

    def _inline_print(*args: Any, **kwargs: Any) -> None:
        str_args = [str(arg) for arg in args]
        print_line = f"{' '.join(str_args)}\n"
        log_buffer.write(print_line)

    wrapped_inputs = wrap_inputs_for_backward_compatibility(inputs)
    exec_globals = {
        "__arg__inputs": wrapped_inputs,
        "__arg__out": None,
        "print": _inline_print,
        "vellum_client": vellum_client,
    }
    run_args = [f"{name}=__arg__inputs['{name}']" for name, value in inputs.items() if value is not undefined]
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
                line_content = lines[frame.lineno - 1]
                # Python 3.13+ uses _lines (plural) instead of _line (singular)
                if sys.version_info >= (3, 13):
                    frame._lines = line_content  # type: ignore[attr-defined]
                else:
                    frame._line = line_content  # type: ignore[attr-defined]

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
