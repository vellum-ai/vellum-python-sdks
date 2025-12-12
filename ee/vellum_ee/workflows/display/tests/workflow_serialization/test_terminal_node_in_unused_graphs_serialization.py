from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input_value: str


class UnusedTerminalNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.input_value


class TerminalNodeInUnusedGraphsWorkflow(BaseWorkflow[Inputs, BaseState]):
    unused_graphs = {UnusedTerminalNode}

    class Outputs(BaseWorkflow.Outputs):
        result = UnusedTerminalNode.Outputs.value


def test_serialize_workflow__terminal_node_in_unused_graphs():
    """
    Tests that a workflow with a single terminal node in unused_graphs serializes correctly.
    """

    # GIVEN a Workflow with a single terminal node in unused_graphs
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=TerminalNodeInUnusedGraphsWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its output variables should contain the terminal node's output
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables[0]["key"] == "result"
    assert output_variables[0]["type"] == "STRING"

    # AND its output values should reference the terminal node's output
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    output_values = workflow_raw_data["output_values"]
    assert len(output_values) == 1
    assert output_values[0]["output_variable_id"] == output_variables[0]["id"]
    assert output_values[0]["value"]["type"] == "NODE_OUTPUT"
