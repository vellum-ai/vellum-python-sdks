import pytest
from unittest.mock import patch

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum.workflows.state.context import WorkflowContext
from vellum_ee.workflows.display.utils.exceptions import UnsupportedSerializationException
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class SimpleClass:
    """A simple class with str and int kwargs in __init__."""

    def __init__(self, name: str, count: int):
        self.name = name
        self.count = count


def test_serialize_workflow__code_tool_with_simple_class_type__raises_error():
    """
    Tests that a serialization error is raised when a code tool has a parameter with a simple class type.
    """

    # GIVEN a function with a simple class parameter
    def my_tool_with_class_param(data: SimpleClass) -> str:
        return data.name

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_class_param]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # WHEN we try to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    # THEN a serialization error should be raised
    with pytest.raises(UnsupportedSerializationException) as exc_info:
        workflow_display.serialize()

    # AND the error message should mention the function name and the failed type
    error_message = str(exc_info.value)
    assert "my_tool_with_class_param" in error_message
    assert "Failed to compile type" in error_message


def test_serialize_workflow__code_tool_with_workflow_context_type__raises_error():
    """
    Tests that a serialization error is raised when a code tool has a WorkflowContext parameter.
    """

    # GIVEN a function with a WorkflowContext parameter
    def my_tool_with_context(ctx: WorkflowContext, query: str) -> str:
        return query

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_context]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # WHEN we try to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)

    # THEN a serialization error should be raised
    with pytest.raises(UnsupportedSerializationException) as exc_info:
        workflow_display.serialize()

    # AND the error message should mention the function name and WorkflowContext
    error_message = str(exc_info.value)
    assert "my_tool_with_context" in error_message
    assert "WorkflowContext" in error_message


def test_serialize_workflow__compile_function_definition_raises_value_error__raises_serialization_error():
    """
    Tests that a ValueError from compile_function_definition is converted to an UnsupportedSerializationException.
    """

    # GIVEN a simple function
    def my_simple_tool(query: str) -> str:
        return query

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_simple_tool]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # AND compile_function_definition is mocked to raise a ValueError
    with patch("vellum_ee.workflows.display.utils.expressions.compile_function_definition") as mock_compile:
        mock_compile.side_effect = ValueError("Failed to compile type: <class 'SomeUnknownType'>")

        # WHEN we try to serialize the workflow
        workflow_display = get_workflow_display(workflow_class=TestWorkflow)

        # THEN a serialization error should be raised
        with pytest.raises(UnsupportedSerializationException) as exc_info:
            workflow_display.serialize()

        # AND the error message should contain the original ValueError message
        error_message = str(exc_info.value)
        assert "my_simple_tool" in error_message
        assert "Failed to compile type" in error_message
