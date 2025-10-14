from typing import List

from vellum import VellumDocument
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    documents: List[VellumDocument]


class MyFinalOutputNode(FinalOutputNode):
    class Outputs(BaseOutputs):
        value = Inputs.documents


class WorkflowWithListVellumDocument(BaseWorkflow[Inputs, BaseState]):
    """A workflow that takes a list of VellumDocument as input."""

    graph = MyFinalOutputNode

    class Outputs(BaseOutputs):
        result = MyFinalOutputNode.Outputs.value


def test_serialize_workflow_with_list_vellum_document():
    """Tests that we can serialize a workflow with List[VellumDocument] input."""

    workflow_display = get_workflow_display(workflow_class=WorkflowWithListVellumDocument)

    # WHEN we serialize it
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1

    input_var = input_variables[0]
    assert input_var["key"] == "documents"
    assert input_var["type"] == "JSON"
    # NOTE: Once custom type serialization is supported, we will want to represent this using an openapi spec
    assert input_var["required"] is True
    assert input_var["default"] is None
    assert input_var["extensions"] == {"color": None}

    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1

    output_var = output_variables[0]
    assert output_var["key"] == "result"

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["nodes"]) == 2
    assert len(workflow_raw_data["edges"]) == 1
