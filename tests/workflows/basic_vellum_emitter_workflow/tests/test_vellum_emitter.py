import pytest
from unittest.mock import Mock, patch

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.state.base import BaseState


class TestState(BaseState):
    test_value: int = 0


@pytest.fixture
def mock_create_vellum_client():
    """Fixture for mocking create_vellum_client."""
    with patch("vellum.workflows.emitters.vellum_emitter.create_vellum_client") as mock:
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


def test_vellum_emitter__happy_path(mock_create_vellum_client, mock_default_serializer):
    """Test VellumEmitter happy path with event emission and state snapshotting."""
    # GIVEN a properly configured VellumEmitter with mocked serialization
    mock_default_serializer.side_effect = [
        {"event": "workflow_initiated_data"},
        {"state": "snapshotted_state_data"},
        "2024-07-31T10:00:00Z",
    ]

    # AND a VellumEmitter initialized with a test API key
    emitter = VellumEmitter(api_key="test-key")

    # AND we have a test workflow event
    mock_event = Mock()
    mock_event.name = "workflow.execution.initiated"

    # AND we have a test state with known values
    test_state = TestState()
    test_state.test_value = 42

    # WHEN we emit the workflow event
    emitter.emit_event(mock_event)

    # AND when we snapshot the state
    emitter.snapshot_state(test_state)

    # THEN the emitter should have made HTTP requests for both operations
    assert mock_create_vellum_client._client_wrapper.httpx_client.request.call_count == 2

    # AND the first call should be for the event emission
    first_call_args = mock_create_vellum_client._client_wrapper.httpx_client.request.call_args_list[0]
    assert first_call_args[1]["method"] == "POST"
    assert first_call_args[1]["path"] == "https://api.vellum.ai/events"
    assert "json" in first_call_args[1]
    assert first_call_args[1]["json"]["type"] == "workflow.event"
    assert first_call_args[1]["json"]["data"] == {"event": "workflow_initiated_data"}

    # AND the second call should be for the state snapshot
    second_call_args = mock_create_vellum_client._client_wrapper.httpx_client.request.call_args_list[1]
    assert second_call_args[1]["method"] == "POST"
    assert second_call_args[1]["path"] == "https://api.vellum.ai/events"
    assert "json" in second_call_args[1]
    assert second_call_args[1]["json"]["type"] == "workflow.state.snapshotted"
    assert second_call_args[1]["json"]["data"] == {"state": "snapshotted_state_data"}

    # AND the serializer should have been called for both the event and state
    assert mock_default_serializer.call_count == 3  # event, state, timestamp


if __name__ == "__main__":
    pytest.main([__file__])
