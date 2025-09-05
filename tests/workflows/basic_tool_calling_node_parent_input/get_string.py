from vellum.workflows.utils.functions import use_tool_inputs

from .inputs import ParentInputs
from .nodes.dummy_node import DummyNode


@use_tool_inputs(
    parent_input=ParentInputs.parent_input,
    dummy_input=DummyNode.Outputs.text,
)
def get_string(parent_input: str, dummy_input: str, populated_input: str) -> str:
    """
    Get a string with the parent input, dummy input, and the populated input.
    """
    return f"This is the parent input: {parent_input}, this is the dummy input: {dummy_input}, and this is the populated input: {populated_input}"  # noqa: E501
