from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.test_parse_error_message.workflow import Inputs, ParseErrorMessageTestWorkflow


def test_parse_error_message__navigates_traceback_to_node_file():
    """
    Test that _parse_error_message navigates the traceback to find the node file.

    When a generic exception is raised from a node, the traceback will include frames
    from vellum.* code. The _parse_error_message logic should navigate backwards through
    the traceback to find the frame in the node file (not in vellum.* code).
    """
    workflow = ParseErrorMessageTestWorkflow()

    terminal_event = workflow.run(Inputs(value="test"))

    assert terminal_event.name == "workflow.execution.rejected"

    assert terminal_event.error is not None
    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION

    assert "Test error from node" in terminal_event.error.message
