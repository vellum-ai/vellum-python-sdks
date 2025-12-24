from vellum.workflows.errors import WorkflowErrorCode

from tests.workflows.chained_node_rejection_with_fulfilled_output.workflow import (
    ChainedNodeRejectionWithFulfilledOutputWorkflow,
)


def test_run_workflow__chained_node_rejection_with_fulfilled_output():
    """
    Tests that a workflow is rejected when a node fails, even if the workflow output
    was already resolved from a successful upstream node.
    """

    # GIVEN a workflow where the first node succeeds and the second node fails,
    # but the workflow output points to the first node's output
    workflow = ChainedNodeRejectionWithFulfilledOutputWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete with a rejection event (not fulfilled)
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the error should be from the second node's failure
    assert terminal_event.error.code == WorkflowErrorCode.USER_DEFINED_ERROR
    assert terminal_event.error.message == "Second node failed"
