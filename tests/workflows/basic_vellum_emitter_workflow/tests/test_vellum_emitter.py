import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.events.workflow import WorkflowExecutionInitiatedBody, WorkflowExecutionInitiatedEvent
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.workflows.base import BaseWorkflow


class TestInputs(BaseInputs):
    foo: str = "bar"


class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
    pass


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
def mock_type_adapter():
    """Fixture for mocking TypeAdapter validation."""
    with patch("vellum.workflows.emitters.vellum_emitter.pydantic.TypeAdapter") as mock:
        mock_adapter = Mock()
        mock.return_value = mock_adapter
        yield mock_adapter


@pytest.fixture
def mock_workflow_context(mock_create_vellum_client):
    """Fixture for creating a mock workflow context."""
    context = WorkflowContext(vellum_client=mock_create_vellum_client)
    return context


def test_vellum_emitter__happy_path(mock_workflow_context, mock_type_adapter):
    """Test VellumEmitter happy path with event emission."""
    # GIVEN a properly configured VellumEmitter with mocked TypeAdapter
    mock_client_event = Mock()
    mock_client_event.name = "workflow.execution.initiated"
    mock_type_adapter.validate_json.return_value = mock_client_event

    # AND a VellumEmitter initialized
    emitter = VellumEmitter()

    # AND the emitter is registered with a workflow context
    emitter.register_context(mock_workflow_context)

    # AND we have a test workflow event
    workflow_initiated_event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test"),
        ),
    )

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

    client_event = call_args[1]["request"]
    assert client_event.name == "workflow.execution.initiated"

    # AND the TypeAdapter should have been called for the event conversion
    assert mock_type_adapter.validate_json.call_count == 1
