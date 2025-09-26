from vellum.workflows.utils.functions import use_tool_inputs

from .inputs import ParentInputs
from .nodes.dummy_node import DummyNode


@use_tool_inputs(
    parent_input=ParentInputs.parent_input,
    dummy_input=DummyNode.Outputs.text,
    constant_input="constant_input",
    unused_input="unused_input",  # this should not be passed to the function
)
def get_string(parent_input: str, dummy_input: str, constant_input: str, populated_input: str) -> str:
    """
    Get a string with the parent input, dummy input, and the populated input.
    """
    return f"parent input: {parent_input}, dummy input: {dummy_input}, constant input: {constant_input}, populated input: {populated_input}"  # noqa: E501
