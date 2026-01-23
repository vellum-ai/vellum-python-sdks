import pytest
from typing import Any, Dict

from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.map_node import MapNode
from vellum.workflows.nodes.core.templating_node import TemplatingNode
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.nodes.displayable.inline_prompt_node import InlinePromptNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.core import Json
from vellum.workflows.workflows.base import BaseWorkflow


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
        == "Failed to validate output type for node 'Output': Output type mismatch: declared type 'list' but "
        "the 'value' Output has type(s) 'str'. "
    )


def test_final_output_node__mismatched_output_type_in_state_should_raise_exception():
    # GIVEN a state with a str type
    class State(BaseState):
        foo: str

    # AND a FinalOutputNode declared with list output type
    class Output(FinalOutputNode[BaseState, list]):
        class Outputs(FinalOutputNode.Outputs):
            value = State.foo

    # WHEN attempting to validate the node class
    # THEN a ValueError should be raised during validation
    with pytest.raises(ValueError) as exc_info:
        Output.__validate__()

    # AND the error message should indicate the type mismatch
    assert (
        str(exc_info.value)
        == "Failed to validate output type for node 'Output': Output type mismatch: declared type 'list' but "
        "the 'value' Output has type(s) 'str'. "
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


def test_final_output_node__dict_and_Dict_should_be_compatible():
    """
    Tests that FinalOutputNode validation recognizes dict and Dict[str, Any] as compatible types.
    """

    # GIVEN a FinalOutputNode declared with dict output type
    # AND the value descriptor has Dict[str, Any] type
    class SomeCustomNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            value: Dict[str, Any]

    class DictOutputNode(FinalOutputNode[BaseState, dict]):
        """Output with dict type."""

        class Outputs(FinalOutputNode.Outputs):
            value = SomeCustomNode.Outputs.value

    # WHEN attempting to validate the node class
    # THEN validation should pass without raising an exception
    try:
        DictOutputNode.__validate__()
    except ValueError as e:
        pytest.fail(f"Validation should not raise an exception for dict/Dict compatibility: {e}")


def test_final_output_node__any_output_type_should_accept_json():
    """
    Tests that FinalOutputNode with Any output type accepts a TemplatingNode with Json output type.
    """

    # GIVEN a TemplatingNode with Json output type
    class JsonTemplatingNode(TemplatingNode[BaseState, Json]):
        """Templating node that outputs Json."""

        template = '{"key": "value"}'

    # AND a FinalOutputNode with Any output type referencing the TemplatingNode
    class AnyOutputNode(FinalOutputNode[BaseState, Any]):
        """Output with Any type."""

        class Outputs(FinalOutputNode.Outputs):
            value = JsonTemplatingNode.Outputs.result

    # WHEN attempting to validate the node class
    # THEN validation should pass without raising an exception
    try:
        AnyOutputNode.__validate__()
    except ValueError as e:
        pytest.fail(f"Validation should not raise an exception when Any accepts Json: {e}")


def test_final_output_node__list_str_output_type_should_pass_validation():
    """
    Tests that FinalOutputNode with list[str] output type accepts a descriptor with List[str] type.
    """

    # GIVEN value descriptor has List[str] type
    class MySubworkflow(BaseWorkflow):
        class Outputs(BaseWorkflow.Outputs):
            result: str

    class MyMap(MapNode):
        subworkflow = MySubworkflow

    # AND a FinalOutputNode declared with list[str] output type
    class ListStrOutputNode(FinalOutputNode[BaseState, list[str]]):
        class Outputs(FinalOutputNode.Outputs):
            value = MyMap.Outputs.result

    # WHEN attempting to validate the node class
    try:
        ListStrOutputNode.__validate__()
    except Exception as e:
        # THEN validation should pass without raising an exception
        pytest.fail(f"Validation should not raise an exception for list[str]/List[str] compatibility: {e}")
