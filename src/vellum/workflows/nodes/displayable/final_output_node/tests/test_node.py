import pytest

from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node import InlinePromptNode
from vellum.workflows.state.base import BaseState


def test_final_output_node__mismatched_output_type_should_raise_exception_when_ran():
    # GIVEN a FinalOutputNode with a mismatched output type
    class StringOutputNode(FinalOutputNode[BaseState, str]):
        class Outputs(FinalOutputNode.Outputs):
            value = {"foo": "bar"}

    # WHEN the node is run
    node = StringOutputNode()
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN an error is raised
    assert str(exc_info.value) == "Expected an output of type 'str', but received 'dict'"


def test_final_output_node__mismatched_output_type_should_raise_exception():
    # GIVEN a FinalOutputNode declared with list output type but has a string value type
    class Output(FinalOutputNode[BaseState, list]):
        """Output the extracted invoice line items as an array of objects."""

        class Outputs(FinalOutputNode.Outputs):
            value = InlinePromptNode.Outputs.text

    # WHEN attempting to validate the node class
    # THEN a ValueError should be raised during validation
    with pytest.raises(ValueError) as exc_info:
        Output.__validate__()

    # AND the error message should indicate the type mismatch
    assert (
        str(exc_info.value)
        == "Output type mismatch in Output: FinalOutputNode is declared with output type 'list' but "
        "the 'value' descriptor has type(s) ['str']. The output descriptor type must match the "
        "declared FinalOutputNode output type."
    )


def test_final_output_node__matching_output_type_should_pass_validation():
    # GIVEN a FinalOutputNode declared with correct matching types
    class CorrectOutput(FinalOutputNode[BaseState, str]):
        """Output with correct type matching."""

        class Outputs(FinalOutputNode.Outputs):
            value = InlinePromptNode.Outputs.text

    # WHEN attempting to validate the node class
    # THEN validation should pass without raising an exception
    try:
        CorrectOutput.__validate__()
    except ValueError:
        pytest.fail("Validation should not raise an exception for correct type matching")
