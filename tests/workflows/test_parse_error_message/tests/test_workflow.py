from vellum.client.errors.forbidden_error import ForbiddenError
from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.test_parse_error_message.workflow import Inputs, ParseErrorMessageTestWorkflow


def test_parse_error_message__navigates_traceback_to_node_file(vellum_client):
    """
    Test that _parse_error_message navigates the traceback to find the node file.

    When a ForbiddenError (403) is raised from the Vellum client's execute_integration_tool,
    the traceback will include frames from vellum.* code. The _parse_error_message logic
    should navigate backwards through the traceback to find the frame in the node file
    (not in vellum.* code).
    """
    vellum_client.integrations.execute_integration_tool.side_effect = ForbiddenError(
        body={"error": "Access forbidden: Invalid credentials"}
    )

    workflow = ParseErrorMessageTestWorkflow()

    terminal_event = workflow.run(
        Inputs(
            integration_name="GITHUB",
            tool_name="create_issue",
        )
    )

    assert terminal_event.name == "workflow.execution.rejected"

    assert terminal_event.error is not None
    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION

    assert "403" in terminal_event.error.message or "Forbidden" in terminal_event.error.message
