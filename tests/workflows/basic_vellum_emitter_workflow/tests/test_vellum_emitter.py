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
    mock_event = Mock()
    mock_event.name = "workflow.execution.initiated"

    # WHEN we emit the workflow event
    emitter.emit_event(mock_event)

    # THEN the emitter should have made HTTP requests for the event
    assert mock_workflow_context.vellum_client._client_wrapper.httpx_client.request.call_count == 1

    # AND the call should be for the event emission
    call_args = mock_workflow_context.vellum_client._client_wrapper.httpx_client.request.call_args_list[0]
    assert call_args[1]["method"] == "POST"
    assert call_args[1]["path"] == "https://api.vellum.ai/events"
    assert "json" in call_args[1]
    assert call_args[1]["json"] == {"event": "workflow_initiated_data"}

    # AND the serializer should have been called for the event
    assert mock_default_serializer.call_count == 1
