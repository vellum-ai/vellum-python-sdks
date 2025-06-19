from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.error_handling_module_path.workflow import CustomErrorWorkflow, VellumAPINode, VellumErrorWorkflow


def test_custom_node_error_returns_node_execution_error():
    """Test that nodes from custom modules return NODE_EXECUTION error"""

    # GIVEN a workflow with that extends a custom node
    workflow = CustomErrorWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we get a user facing node execution error
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION
    assert terminal_event.error.message == "User defined error"


def test_vellum_node_error_returns_internal_error():
    """Test that nodes from vellum modules return INTERNAL_ERROR with generic message"""

    # GIVEN a workflow with that extends a Vellum Node
    workflow = VellumErrorWorkflow()

    # AND we hack the node in a way that will cause it to raise an exception from within the node
    VellumAPINode._validate = None  # type: ignore

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we get an internal error
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert terminal_event.error.message == "Internal error"
