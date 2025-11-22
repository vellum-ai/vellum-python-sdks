import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_workflow_serialization_error__node_points_to_itself():
    """
    Tests that serialization raises an error when a node creates an infinite loop by pointing to itself.
    """

    # GIVEN a simple workflow where a node points to itself
    class StartNode(BaseNode[BaseState]):
        pass

    class InfiniteLoopWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = StartNode >> StartNode

    # WHEN we attempt to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=InfiniteLoopWorkflow)

    # THEN it should raise a WorkflowValidationError about the self-edge
    with pytest.raises(WorkflowValidationError) as exc_info:
        workflow_display.serialize()

    # AND the error message should be exact and descriptive
    error_message = str(exc_info.value)
    assert error_message == (
        "Workflow validation error in InfiniteLoopWorkflow: " "Graph contains a self-edge (StartNode >> StartNode)."
    )
