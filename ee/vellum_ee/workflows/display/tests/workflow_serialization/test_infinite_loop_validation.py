import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.ports.port import Port
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


def test_workflow_serialization__node_with_conditional_loop_is_valid():
    """
    Tests that a node with conditional ports (one looping back, one going forward) is valid.
    """

    # GIVEN a workflow where a node has ports with one looping back to itself and one going to another node
    class State(BaseState):
        should_loop: bool = False

    class StartNode(BaseNode[State]):
        class Ports(BaseNode.Ports):
            loop = Port.on_if(State.should_loop.equals(True))
            end = Port.on_else()

    class EndNode(BaseNode[State]):
        pass

    class ConditionalLoopWorkflow(BaseWorkflow[BaseInputs, State]):
        graph = {
            StartNode.Ports.loop >> StartNode,
            StartNode.Ports.end >> EndNode,
        }

    # WHEN we attempt to serialize the workflow
    workflow_display = get_workflow_display(workflow_class=ConditionalLoopWorkflow)

    # THEN it should NOT raise a WorkflowValidationError
    result = workflow_display.serialize()
    assert result is not None
