"""Utility functions for parsing exceptions into structured serialization errors."""

import re
import traceback
from typing import Any, Dict, Optional

from vellum_ee.workflows.display.workflows.base_workflow_display import SerializationError


def parse_exception_to_structured_error(
    exc: Exception,
    files: Dict[str, str],
    namespace: str,
    include_debug: bool = False,
) -> SerializationError:
    """
    Parse an exception into a structured serialization error with file context.

    Args:
        exc: The exception to parse
        files: Dictionary mapping file paths to their contents
        namespace: The random namespace used for this serialization (e.g., "AtUlfaZJaEHC6U")
        include_debug: Whether to include full traceback and namespace info

    Returns:
        SerializationError with file path, line number, code snippet, and suggestions
    """
    tb = traceback.extract_tb(exc.__traceback__)
    frame = find_user_code_frame(tb, namespace)

    if frame:
        actual_file = map_namespace_to_file(frame.filename, namespace)
        line_no = frame.lineno
        snippet = extract_code_snippet(files, actual_file, line_no)
    else:
        # Fallback if we can't find a user code frame
        actual_file = "workflow.py"
        line_no = None
        snippet = None

    error_message = enhance_error_message(exc, frame, files) if frame else str(exc)
    suggestion = generate_suggestion(exc, actual_file)

    error_dict: Dict[str, Any] = {
        "file": actual_file,
        "line": line_no,
        "error_type": type(exc).__name__,
        "message": error_message,
        "code_snippet": snippet,
        "suggestion": suggestion,
    }

    if include_debug:
        error_dict["debug"] = {
            "full_traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            "namespace": namespace,
        }

    return SerializationError(**error_dict)


def map_namespace_to_file(path: str, namespace: str) -> str:
    """
    Convert namespace module path to actual file path.

    Example: "AtUlfaZJaEHC6U.nodes.tools" -> "nodes/tools.py"

    Args:
        path: The module path from the traceback
        namespace: The random namespace prefix

    Returns:
        Relative file path
    """
    if not path.startswith(namespace):
        return path

    # Remove namespace prefix
    rel = path[len(namespace) + 1 :]  # +1 for the dot
    # Convert module path to file path
    return rel.replace(".", "/") + ".py"


def find_user_code_frame(tb: traceback.StackSummary, namespace: str) -> Optional[traceback.FrameSummary]:
    """
    Find the first frame that is in user code (not SDK code).

    Args:
        tb: The traceback stack summary
        namespace: The random namespace to identify user code

    Returns:
        The first user code frame, or None if not found
    """
    for frame in tb:
        # User code is identified by the namespace prefix
        if namespace in frame.filename:
            return frame

    # Fallback to last frame if no user code found
    return tb[-1] if tb else None


def extract_code_snippet(
    files: Dict[str, str], file_path: str, line_no: Optional[int], context_lines: int = 2
) -> Optional[str]:
    """
    Extract a code snippet from the file with surrounding context.

    Args:
        files: Dictionary mapping file paths to their contents
        file_path: The file to extract from
        line_no: The line number of the error
        context_lines: Number of lines to show before/after

    Returns:
        Code snippet with line numbers, or None if not found
    """
    if not line_no or file_path not in files:
        return None

    lines = files[file_path].split("\n")
    if line_no > len(lines):
        return None

    # Get context (line_no is 1-indexed)
    start_line = max(1, line_no - context_lines)
    end_line = min(len(lines), line_no + context_lines)

    snippet_lines = []
    for i in range(start_line, end_line + 1):
        prefix = "→ " if i == line_no else "  "
        snippet_lines.append(f"{prefix}{i:4d} | {lines[i-1]}")

    return "\n".join(snippet_lines)


def enhance_error_message(exc: Exception, frame: Optional[traceback.FrameSummary], files: Dict[str, str]) -> str:
    """
    Enhance error message with additional context when possible.

    Args:
        exc: The exception
        frame: The traceback frame
        files: File contents

    Returns:
        Enhanced error message
    """
    base_message = str(exc)

    # For NameError, try to provide more context
    if isinstance(exc, NameError) and frame:
        # Extract the undefined name from the error message
        match = re.search(r"name '(\w+)' is not defined", base_message)
        if match:
            undefined_name = match.group(1)
            # Check if this looks like a class that should be imported
            if undefined_name[0].isupper():
                return f"{base_message}. This looks like a class - did you forget to import it?"

    return base_message


def generate_suggestion(exc: Exception, file_path: str) -> Optional[str]:
    """
    Generate a helpful suggestion based on the error type and context.

    Args:
        exc: The exception
        file_path: The file where the error occurred

    Returns:
        Helpful suggestion, or None
    """
    error_type = type(exc).__name__
    error_msg = str(exc)

    if error_type == "NameError":
        match = re.search(r"name '(\w+)' is not defined", error_msg)
        if match:
            name = match.group(1)
            if name[0].isupper():
                return f"Did you forget to import {name}?"
            return f"Check if '{name}' is defined before use"

    elif error_type == "ImportError" or error_type == "ModuleNotFoundError":
        match = re.search(r"No module named '(\w+)'", error_msg)
        if match:
            module = match.group(1)
            return f"Ensure '{module}' is installed or check the import path"

    elif error_type == "AttributeError":
        match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_msg)
        if match:
            obj_type, attr = match.groups()
            return f"Check if '{attr}' exists on {obj_type} objects"

    elif error_type == "TypeError":
        if "required positional argument" in error_msg:
            return "Check that all required arguments are provided"
        if "__init__()" in error_msg:
            return "Check the constructor arguments"

    elif error_type == "SyntaxError":
        return "Fix the syntax error in the code"

    elif error_type == "IndentationError":
        return "Check the indentation of your code"

    return None
