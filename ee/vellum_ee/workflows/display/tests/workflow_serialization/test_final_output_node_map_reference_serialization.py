from typing import List

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class TestInputs(BaseInputs):
    items: List[str]


class TestIteration(BaseNode):
    item = MapNode.SubworkflowInputs.item
    index = MapNode.SubworkflowInputs.index

    class Outputs(BaseOutputs):
        processed: str

    def run(self) -> Outputs:
        return self.Outputs(processed=f"processed_{self.item}_{self.index}")


class TestIterationSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = TestIteration

    class Outputs(BaseOutputs):
        processed = TestIteration.Outputs.processed


class TestMapNode(MapNode):
    items = TestInputs.items
    subworkflow = TestIterationSubworkflow


class TestFinalOutputNode(FinalOutputNode[BaseState, List[str]]):
    class Outputs(FinalOutputNode.Outputs):
        value = TestMapNode.Outputs.processed


class TestWorkflowWithFinalOutputReferencingMap(BaseWorkflow[TestInputs, BaseState]):
    graph = TestMapNode >> TestFinalOutputNode

    class Outputs(BaseOutputs):
        final_result = TestFinalOutputNode.Outputs.value


def test_serialize_workflow__final_output_node_referencing_map_node():
    """
    Test that final output nodes referencing map node outputs have correct outputs structure.

    This test verifies that when a FinalOutputNode references a MapNode output,
    the serialized output contains proper NODE_OUTPUT references instead of None values.
    This addresses the Agent Builder issue where final outputs showed value=None in the UI.
    """
    workflow_display = get_workflow_display(workflow_class=TestWorkflowWithFinalOutputReferencingMap)

    # WHEN we serialize it
    serialized_workflow: dict = workflow_display.serialize()

    # THEN the final output node should have the correct outputs structure
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    map_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "MAP")
    final_output_node = next(node for node in workflow_raw_data["nodes"] if node["type"] == "TERMINAL")

    # AND the map node's subworkflow should have the one output variable
    output_variable = next(iter(map_node["data"]["output_variables"]))
    map_node_output_id = output_variable["id"]

    # AND the final output node should have an outputs array with proper structure
    assert "outputs" in final_output_node
    outputs = final_output_node["outputs"]
    assert len(outputs) == 1

    output = outputs[0]
    # AND the output should have the correct structure with NODE_OUTPUT reference instead of None
    assert output["name"] == "value"
    assert output["type"] == "JSON"

    # AND the value should be a NODE_OUTPUT reference, not None
    assert output["value"] is not None, f"Expected NODE_OUTPUT reference but got None. Full output: {output}"
    assert output["value"]["type"] == "NODE_OUTPUT", f"Expected NODE_OUTPUT type but got {output['value']['type']}"
    assert "node_id" in output["value"], f"Missing node_id in output value: {output['value']}"
    assert output["value"]["node_output_id"] == map_node_output_id
