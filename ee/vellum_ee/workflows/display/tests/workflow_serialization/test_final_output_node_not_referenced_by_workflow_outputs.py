import pytest

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow
from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class Inputs(BaseInputs):
    input_value: str


class UnreferencedFinalOutputNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.input_value


class WorkflowWithUnreferencedFinalOutputNode(BaseWorkflow[Inputs, BaseState]):
    graph = UnreferencedFinalOutputNode

    class Outputs(BaseWorkflow.Outputs):
        # Intentionally NOT referencing UnreferencedFinalOutputNode.Outputs.value
        result = Inputs.input_value


def test_serialize_workflow__final_output_node_not_referenced_by_workflow_outputs():
    """
    Tests that serialization raises a WorkflowValidationError when a workflow has a final output node
    but the workflow outputs don't reference it.
    """

    # GIVEN a Workflow with a FinalOutputNode that is not referenced by workflow outputs
    workflow_display = get_workflow_display(workflow_class=WorkflowWithUnreferencedFinalOutputNode)

    # WHEN we serialize it
    # THEN it should raise a WorkflowValidationError about unreferenced terminal nodes
    with pytest.raises(WorkflowValidationError) as exc_info:
        workflow_display.serialize()

    # AND the error message should indicate the terminal node is not referenced
    error_message = str(exc_info.value)
    assert "WorkflowWithUnreferencedFinalOutputNode" in error_message
    assert "terminal nodes that are not referenced by workflow outputs" in error_message
