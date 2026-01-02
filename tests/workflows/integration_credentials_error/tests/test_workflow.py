from vellum.client.core.api_error import ApiError
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.integration_credentials_error.workflow import IntegrationCredentialsErrorWorkflow


def test_integration_credentials_error__node_rejected_event_contains_raw_data(vellum_client):
    """
    Tests that when a base node executes an integration action and a 403 ApiError is raised,
    the node rejected event's raw_data contains enough information for the UI to render
    the INTEGRATION_CREDENTIALS_UNAVAILABLE error.
    """
    # GIVEN the integration API raises a 403 error with integration details
    # This matches the actual Django API response from ExecuteToolUnresolvableCredentialResponseSerializer
    # which returns {"message": "...", "integration": {...}} without a "code" field
    structured_error_body = {
        "message": "You must authenticate with this integration before you can execute this tool.",
        "integration": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "provider": "COMPOSIO",
            "name": "GITHUB",
        },
    }
    vellum_client.integrations.execute_integration_tool.side_effect = ApiError(
        status_code=403,
        body=structured_error_body,
    )

    # AND a workflow with a node that executes an integration action
    workflow = IntegrationCredentialsErrorWorkflow()

    # WHEN the workflow is streamed
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # THEN we should find a node rejected event
    node_rejected_events = [e for e in events if e.name == "node.execution.rejected"]
    assert len(node_rejected_events) == 1
    node_rejected_event = node_rejected_events[0]

    # AND the error code should be INTEGRATION_CREDENTIALS_UNAVAILABLE
    assert node_rejected_event.error.code == WorkflowErrorCode.INTEGRATION_CREDENTIALS_UNAVAILABLE

    # AND the error message should match the backend response
    assert "You must authenticate with this integration" in node_rejected_event.error.message

    # AND the raw_data should contain integration details for the UI to render the error
    assert node_rejected_event.error.raw_data is not None
    assert "integration" in node_rejected_event.error.raw_data

    # AND the integration details should be accessible
    integration = node_rejected_event.error.raw_data["integration"]
    assert integration["id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert integration["provider"] == "COMPOSIO"
    assert integration["name"] == "GITHUB"
