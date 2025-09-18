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
