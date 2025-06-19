from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.error_handling_module_path.workflow import CustomErrorWorkflow, VellumErrorWorkflow


def test_custom_node_error_returns_node_execution_error():
    """Test that nodes from custom modules return NODE_EXECUTION error"""
    workflow = CustomErrorWorkflow()

    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION
    assert "User configuration error: Invalid API endpoint" in str(terminal_event.error.message)


def test_vellum_node_error_returns_internal_error():
    """Test that nodes from vellum modules return INTERNAL_ERROR with generic message"""
    workflow = VellumErrorWorkflow()

    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert terminal_event.error.message == "Internal error"
