import pytest
from typing import Optional

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.inline_prompt_node.node import InlinePromptNode
from vellum.workflows.nodes.displayable.tool_calling_node.node import ToolCallingNode
from vellum_ee.workflows.display.utils.exceptions import UnsupportedSerializationException
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_serialize_workflow__code_tool_with_node_reference__raises_error():
    """
    Tests that a serialization error is raised when a code tool references a workflow node.
    """

    # GIVEN a function that references a node class
    def my_tool_with_node_reference(query: str) -> str:
        return str(InlinePromptNode)

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_node_reference]

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

    # AND the error message should mention the node class and provide guidance
    error_message = str(exc_info.value)
    assert "InlinePromptNode" in error_message
    assert "Code tools cannot reference workflow nodes" in error_message
    assert "Inline Subworkflow tool" in error_message


def test_serialize_workflow__code_tool_without_node_reference__no_error():
    """
    Tests that no error is raised when a code tool does not reference any workflow nodes,
    even if the module has node imports at the top level.
    """

    # GIVEN a function that does NOT reference any node class (even though InlinePromptNode
    # is imported at the module level)
    def my_simple_tool(query: str) -> str:
        return query.upper()

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_simple_tool]

    # AND a workflow with the tool calling node
    class TestWorkflow(BaseWorkflow):
        graph = MyToolCallingNode

        class Outputs(BaseWorkflow.Outputs):
            result = MyToolCallingNode.Outputs.text

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=TestWorkflow)
    serialized_workflow = workflow_display.serialize()

    # THEN no error should be raised and the workflow should serialize successfully
    assert serialized_workflow is not None
    assert "workflow_raw_data" in serialized_workflow


def test_serialize_workflow__code_tool_with_node_default_arg__raises_error():
    """
    Tests that a serialization error is raised when a code tool has a node class as a default argument.
    """

    # GIVEN a function with a node class as a default argument
    def my_tool_with_node_default(query: str, node=InlinePromptNode) -> str:
        return node.__name__

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_node_default]

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

    # AND the error message should mention the node class
    error_message = str(exc_info.value)
    assert "InlinePromptNode" in error_message
    assert "Code tools cannot reference workflow nodes" in error_message


def test_serialize_workflow__code_tool_with_node_kwonly_default__raises_error():
    """
    Tests that a serialization error is raised when a code tool has a node class as a keyword-only default.
    """

    # GIVEN a function with a node class as a keyword-only default argument
    def my_tool_with_node_kwdefault(query: str, *, node=InlinePromptNode) -> str:
        return node.__name__

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_node_kwdefault]

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

    # AND the error message should mention the node class
    error_message = str(exc_info.value)
    assert "InlinePromptNode" in error_message
    assert "Code tools cannot reference workflow nodes" in error_message


def test_serialize_workflow__code_tool_with_node_annotation__raises_error():
    """
    Tests that a serialization error is raised when a code tool has a node class in its type annotations.
    """

    # GIVEN a function with a node class in its type annotations
    def my_tool_with_node_annotation(query: str, node: InlinePromptNode) -> str:
        return query

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_node_annotation]

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

    # AND the error message should mention the node class
    error_message = str(exc_info.value)
    assert "InlinePromptNode" in error_message
    assert "Code tools cannot reference workflow nodes" in error_message


def test_serialize_workflow__code_tool_with_optional_node_annotation__raises_error():
    """
    Tests that a serialization error is raised when a code tool has a node class in an Optional type annotation.
    """

    # GIVEN a function with a node class in an Optional type annotation
    def my_tool_with_optional_node(query: str, node: Optional[InlinePromptNode] = None) -> str:
        return query

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool_with_optional_node]

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

    # AND the error message should mention the node class
    error_message = str(exc_info.value)
    assert "InlinePromptNode" in error_message
    assert "Code tools cannot reference workflow nodes" in error_message


def test_serialize_workflow__code_tool_with_node_instantiation__raises_error():
    """
    Tests that a serialization error is raised when a code tool instantiates a node and calls its run method.
    """

    # GIVEN a function that instantiates a node and calls its run method
    def my_tool():
        node = InlinePromptNode()
        return node.run()

    # AND a tool calling node that uses this function
    class MyToolCallingNode(ToolCallingNode):
        functions = [my_tool]

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

    # AND the error message should mention the node class
    error_message = str(exc_info.value)
    assert "InlinePromptNode" in error_message
    assert "Code tools cannot reference workflow nodes" in error_message
