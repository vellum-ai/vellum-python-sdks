from datetime import datetime, timezone
import json
import time
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


def test_vellum_emitter__happy_path(mock_httpx_transport):
    """Test VellumEmitter happy path with event emission."""

    # GIVEN a properly configured VellumEmitter
    emitter = VellumEmitter()
    workflow_context = WorkflowContext()
    emitter.register_context(workflow_context)

    # AND we have a test workflow event from the SDK
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

    time.sleep(0.15)

    # THEN the emitter should have called client.events.create
    assert mock_httpx_transport.handle_request.call_count == 1

    # AND the call should be for the event emission
    call_args = mock_httpx_transport.handle_request.call_args_list[0]
    mocked_request = call_args[0][0]
    assert mocked_request.method == "POST"
    assert mocked_request.url == "https://api.vellum.ai/monitoring/v1/events"
    assert json.loads(mocked_request.content) == {
        "name": "workflow.execution.initiated",
        "api_version": "2024-10-25",
        "body": {
            "inputs": {"foo": "test"},
            "workflow_definition": {
                "id": "898d564e-2ca3-4b4e-8ee4-51404b7d48bf",
                "module": ["tests", "workflows", "basic_vellum_emitter_workflow", "tests", "test_vellum_emitter"],
                "name": "TestWorkflow",
            },
        },
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "span_id": "123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2024-01-01T12:00:00Z",
        "trace_id": "123e4567-e89b-12d3-a456-426614174000",
    }
