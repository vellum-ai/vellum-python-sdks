from typing import Any

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input: Any


class AnyFinalOutputNode(FinalOutputNode[BaseState, Any]):
    class Outputs(FinalOutputNode.Outputs):
        value: Any = Inputs.input


class AnyFinalOutputNodeWorkflow(BaseWorkflow[Inputs, BaseState]):
    graph = AnyFinalOutputNode

    class Outputs(BaseWorkflow.Outputs):
        value = AnyFinalOutputNode.Outputs.value


def test_serialize_workflow_with_any_output_type():
    """
    Tests that a terminal node with Any output type can be serialized correctly.
    """
    # GIVEN a Workflow that uses a Final Output Node with Any type
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=AnyFinalOutputNodeWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    terminal_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "TERMINAL")
    assert terminal_node["data"]["output_type"] == "JSON"

    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables[0]["type"] == "JSON"
