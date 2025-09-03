from vellum.workflows.utils.functions import use_tool_inputs

from .inputs import ParentInputs


@use_tool_inputs(
    parent_input=ParentInputs.parent_input,
)
def get_string(parent_input: str, populated_input: str) -> str:
    """
    Get a string with the parent input and the populated input.
    """
    return f"This is the parent input: {parent_input} and this is the populated input: {populated_input}"
