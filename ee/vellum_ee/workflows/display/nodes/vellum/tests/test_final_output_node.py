from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_final_output_node_display__serialize_with_valid_types():
    # GIVEN a node that outputs a str
    class StringNode(BaseNode):

        class Outputs:
            result: str

    # AND a FinalOutputNode with matching type to that node
    class CorrectOutput(FinalOutputNode[BaseState, str]):
        class Outputs(FinalOutputNode.Outputs):
            value = StringNode.Outputs.result

    # AND a workflow referencing the node
    class MyWorkflow(BaseWorkflow):
        graph = StringNode >> CorrectOutput

        class Outputs(BaseWorkflow.Outputs):
            final_result = CorrectOutput.Outputs.value

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)

    # THEN serialization should succeed without raising validation errors
    serialized_workflow: dict = workflow_display.serialize()

    # AND the node should be properly serialized
    assert "workflow_raw_data" in serialized_workflow
    assert "nodes" in serialized_workflow["workflow_raw_data"]

    # Find the terminal node in the serialized output
    terminal_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "TERMINAL"
    )
    assert terminal_node is not None
    assert terminal_node["id"] == str(CorrectOutput.__id__)


def test_final_output_node_display__serialize_with_invalid_types_should_raise_error():
    # GIVEN a node that outputs a str
    class StringNode(BaseNode):

        class Outputs:
            result: str

    # AND a FinalOutputNode with mismatched types (expects list but gets str)
    class BadOutput(FinalOutputNode[BaseState, list]):
        """Output with type mismatch."""

        class Outputs(FinalOutputNode.Outputs):
            value = StringNode.Outputs.result  # str type, conflicts with list

    # AND a workflow referencing the node
    class MyWorkflow(BaseWorkflow):
        graph = StringNode >> BadOutput

        class Outputs(BaseWorkflow.Outputs):
            final_result = BadOutput.Outputs.value

    # WHEN we attempt to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)

    # THEN serialization should complete without raising an exception
    serialized_workflow = workflow_display.serialize()

    # AND the error should be captured in workflow_display.errors
    errors = list(workflow_display.display_context.errors)
    assert len(errors) == 1
    assert "Output type mismatch" in str(errors[0])
    assert "list" in str(errors[0])
    assert "str" in str(errors[0])

    # AND the serialized workflow should still be created
    assert "workflow_raw_data" in serialized_workflow


def test_final_output_node_display__serialize_with_list_str_type():
    """
    Tests that FinalOutputNode with list[str] as second type parameter serializes correctly.
    """

    # GIVEN a node that outputs a list of strings
    class ListNode(BaseNode):

        class Outputs:
            result: list[str]

    # AND a FinalOutputNode with list[str] as the second type parameter
    class ListOutput(FinalOutputNode[BaseState, list[str]]):
        class Outputs(FinalOutputNode.Outputs):
            value = ListNode.Outputs.result

    # AND a workflow referencing the node
    class MyWorkflow(BaseWorkflow):
        graph = ListNode >> ListOutput

        class Outputs(BaseWorkflow.Outputs):
            final_result = ListOutput.Outputs.value

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=MyWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN serialization should succeed without raising validation errors
    assert "workflow_raw_data" in serialized_workflow
    assert "nodes" in serialized_workflow["workflow_raw_data"]

    # AND the terminal node should be properly serialized
    terminal_node = next(
        node for node in serialized_workflow["workflow_raw_data"]["nodes"] if node["type"] == "TERMINAL"
    )
    assert terminal_node is not None
    assert terminal_node["id"] == str(ListOutput.__id__)

    # AND the output type should be correctly serialized as ARRAY
    assert terminal_node["data"]["output_type"] == "ARRAY"

    # AND the outputs should contain the correct type information
    assert len(terminal_node["outputs"]) == 1
    assert terminal_node["outputs"][0]["type"] == "ARRAY"

    # AND the output should have an inline type reference with JSON Schema
    schema = terminal_node["outputs"][0]["schema"]
    assert schema["type"] == "array"
    assert schema["items"]["type"] == "string"
