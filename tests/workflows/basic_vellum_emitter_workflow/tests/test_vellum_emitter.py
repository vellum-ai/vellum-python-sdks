import pytest
from unittest.mock import Mock, patch

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext


class TestState(BaseState):
    test_value: int = 0


@pytest.fixture
def mock_create_vellum_client():
    """Fixture for mocking create_vellum_client."""
    with patch("vellum.workflows.vellum_client.create_vellum_client") as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        mock_client._client_wrapper.get_environment.return_value.default = "https://api.vellum.ai"
        mock_client._client_wrapper.get_headers.return_value = {"Authorization": "Bearer test"}

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client._client_wrapper.httpx_client.request.return_value = mock_response

        yield mock_client


@pytest.fixture
def mock_default_serializer():
    """Fixture for mocking default_serializer."""
    with patch("vellum.workflows.emitters.vellum_emitter.default_serializer") as mock:
        yield mock


@pytest.fixture
def mock_workflow_context(mock_create_vellum_client):
    """Fixture for creating a mock workflow context."""
    context = WorkflowContext(vellum_client=mock_create_vellum_client)
    return context


def test_vellum_emitter__happy_path(mock_workflow_context, mock_default_serializer):
    """Test VellumEmitter happy path with event emission."""
    # GIVEN a properly configured VellumEmitter with mocked serialization
    mock_default_serializer.return_value = {"event": "workflow_initiated_data"}

    # AND a VellumEmitter initialized
    emitter = VellumEmitter()

    # AND the emitter is registered with a workflow context
    emitter.register_context(mock_workflow_context)

    # AND we have a test workflow event
    workflow_initiated_event = Mock()
    workflow_initiated_event.name = "workflow.execution.initiated"
    workflow_initiated_event.id = "test-event-id"
    workflow_initiated_event.timestamp = "2024-01-01T12:00:00Z"
    workflow_initiated_event.trace_id = "test-trace-id"
    workflow_initiated_event.span_id = "test-span-id"
    workflow_initiated_event.parent = None

    mock_body = Mock()
    mock_workflow_definition = Mock()
    mock_inputs = Mock()
    mock_body.workflow_definition = mock_workflow_definition
    mock_body.inputs = mock_inputs
    workflow_initiated_event.body = mock_body

    def mock_serializer_side_effect(obj):
        if obj == mock_workflow_definition:
            return {"name": "TestWorkflow", "module": ["test", "module"], "id": "workflow-def-id"}
        elif obj == mock_inputs:
            return {"input_key": "input_value"}
        else:
            return {"event": "workflow_initiated_data"}

    mock_default_serializer.side_effect = mock_serializer_side_effect

    # WHEN we emit the workflow event
    emitter.emit_event(workflow_initiated_event)

    # THEN the emitter should have called client.events.create
    assert mock_workflow_context.vellum_client.events.create.call_count == 1

    # AND the call should be for the event emission via client.events.create
    call_args = mock_workflow_context.vellum_client.events.create.call_args_list[0]
    assert "request" in call_args[1]
    assert "request_options" in call_args[1]

    request_options = call_args[1]["request_options"]
    assert request_options["timeout_in_seconds"] == 30.0
    assert request_options["max_retries"] == 3

    sdk_event = call_args[1]["request"]
    assert sdk_event.name == "workflow.execution.initiated"
    assert hasattr(sdk_event, "id")
    assert hasattr(sdk_event, "timestamp")
    assert hasattr(sdk_event, "trace_id")
    assert hasattr(sdk_event, "span_id")

    # AND the serializer should have been called for the event conversion
    assert mock_default_serializer.call_count >= 1
