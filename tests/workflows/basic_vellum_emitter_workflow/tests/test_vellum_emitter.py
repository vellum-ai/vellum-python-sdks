import pytest
import os
from unittest.mock import Mock, patch

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class TestState(BaseState):
    test_value: int = 0


def test_vellum_emitter_initialization():
    """Test that VellumEmitter can be initialized properly."""
    # Test with enabled=False (should not try to create client)
    emitter = VellumEmitter(enabled=False)
    assert not emitter._enabled

    # Test with invalid API key (should disable gracefully)
    with patch.dict(os.environ, {"VELLUM_API_KEY": ""}):
        emitter = VellumEmitter()
        # Should still initialize but be disabled due to missing API key


def test_vellum_emitter_disabled():
    """Test that disabled emitter doesn't make any requests."""
    emitter = VellumEmitter(enabled=False)

    mock_event = Mock()
    mock_event.name = "test.event"

    # These should not raise any exceptions or make any calls
    emitter.emit_event(mock_event)
    emitter.snapshot_state(TestState())


@patch("vellum.workflows.emitters.vellum_emitter.create_vellum_client")
@patch("vellum.workflows.emitters.vellum_emitter.default_serializer")
def test_vellum_emitter_event_serialization(mock_serializer, mock_create_client):
    """Test that events are serialized correctly."""
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    mock_client._client_wrapper.get_environment.return_value.default = "https://api.vellum.ai"
    mock_client._client_wrapper.get_headers.return_value = {"Authorization": "Bearer test"}

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_client._client_wrapper.httpx_client.request.return_value = mock_response

    mock_serializer.return_value = {"event": "data"}

    emitter = VellumEmitter(api_key="test-key")

    mock_event = Mock()
    mock_event.name = "workflow.execution.initiated"

    emitter.emit_event(mock_event)

    mock_client._client_wrapper.httpx_client.request.assert_called_once()
    call_args = mock_client._client_wrapper.httpx_client.request.call_args

    assert call_args[1]["method"] == "POST"
    assert call_args[1]["path"] == "https://api.vellum.ai/events"
    assert "json" in call_args[1]
    assert call_args[1]["json"]["type"] == "workflow.event"
    assert call_args[1]["json"]["data"] == {"event": "data"}


@patch("vellum.workflows.emitters.vellum_emitter.create_vellum_client")
@patch("vellum.workflows.emitters.vellum_emitter.default_serializer")
def test_vellum_emitter_state_serialization(mock_serializer, mock_create_client):
    """Test that state snapshots are serialized correctly."""
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    mock_client._client_wrapper.get_environment.return_value.default = "https://api.vellum.ai"
    mock_client._client_wrapper.get_headers.return_value = {"Authorization": "Bearer test"}

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_client._client_wrapper.httpx_client.request.return_value = mock_response

    # Mock the serializer to return different values for different calls
    mock_serializer.side_effect = [{"state": "data"}, "2024-07-31T10:00:00Z"]

    emitter = VellumEmitter(api_key="test-key")

    # Create a test state
    state = TestState()
    state.test_value = 42

    # Snapshot the state
    emitter.snapshot_state(state)

    # Verify the HTTP request was made
    mock_client._client_wrapper.httpx_client.request.assert_called_once()
    call_args = mock_client._client_wrapper.httpx_client.request.call_args

    assert call_args[1]["method"] == "POST"
    assert call_args[1]["path"] == "https://api.vellum.ai/events"
    assert "json" in call_args[1]
    assert call_args[1]["json"]["type"] == "workflow.state.snapshotted"
    assert call_args[1]["json"]["data"] == {"state": "data"}


@patch("vellum.workflows.emitters.vellum_emitter.create_vellum_client")
def test_vellum_emitter_error_handling(mock_create_client):
    """Test that emitter handles errors gracefully."""
    mock_client = Mock()
    mock_create_client.return_value = mock_client
    mock_client._client_wrapper.get_environment.return_value.default = "https://api.vellum.ai"
    mock_client._client_wrapper.get_headers.return_value = {"Authorization": "Bearer test"}

    from httpx import HTTPStatusError

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_client._client_wrapper.httpx_client.request.side_effect = HTTPStatusError(
        "Server Error", request=Mock(), response=mock_response
    )

    emitter = VellumEmitter(api_key="test-key", max_retries=0)

    mock_event = Mock()
    mock_event.name = "test.event"

    # This should not raise an exception (errors are logged but not propagated)
    emitter.emit_event(mock_event)


def test_vellum_emitter_usage_pattern():
    """Test the intended usage pattern for VellumEmitter."""

    # This demonstrates how users would use the VellumEmitter
    class MyWorkflow(BaseWorkflow):
        emitters = [VellumEmitter()]

    # Verify an instance of VellumEmitter is in the emitters list
    assert any(isinstance(e, VellumEmitter) for e in MyWorkflow.emitters)


if __name__ == "__main__":
    pytest.main([__file__])
