import pytest

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
        node: InlinePromptNode = InlinePromptNode()
        return str(node)

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
    assert "inline subworkflow tool" in error_message
