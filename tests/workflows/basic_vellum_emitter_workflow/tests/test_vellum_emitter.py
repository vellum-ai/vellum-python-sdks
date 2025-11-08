from datetime import datetime, timezone
import json
import threading
import time
from uuid import UUID

from vellum.client.types import EventCreateResponse
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
    emitter = VellumEmitter(debounce_timeout=0.01)
    workflow_context = WorkflowContext()
    emitter.register_context(workflow_context)

    # AND we have a test workflow with the emitter
    workflow = TestWorkflow(emitters=[emitter])

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

    workflow.join()

    # THEN the emitter should have called client.events.create
    assert mock_httpx_transport.handle_request.call_count == 1

    # AND the call should be for the event emission
    call_args = mock_httpx_transport.handle_request.call_args_list[0]
    mocked_request = call_args[0][0]
    assert mocked_request.method == "POST"
    assert mocked_request.url == "https://api.vellum.ai/monitoring/v1/events"
    assert json.loads(mocked_request.content) == [
        {
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
    ]


def test_vellum_emitter__join_returns_quickly_despite_slow_http_request(mocker):
    """
    Test that emitter.join() returns quickly even when HTTP request is slow.

    This test verifies the fix for the issue where workflow.join() was blocking
    for 10+ seconds waiting for monitoring events to be sent. After the fix,
    join() should return immediately (< 0.5s) even if the HTTP request takes
    1 second, because events are sent asynchronously in a background thread.

    Before the fix: This test would fail because join() would block for ~1 second.
    After the fix: This test passes because join() returns immediately.
    """
    # GIVEN a properly configured VellumEmitter
    emitter = VellumEmitter(debounce_timeout=0.01)
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

    # AND we mock client.events.create to take 1 second (simulating slow network/server)
    http_request_started = threading.Event()
    http_request_completed = threading.Event()

    def slow_events_create(*args, **kwargs):
        """Simulate a slow HTTP request that takes 1 second."""
        http_request_started.set()
        time.sleep(1.0)  # Simulate slow HTTP request
        http_request_completed.set()
        return EventCreateResponse(count=1)

    # Mock the create method directly
    mock_create = mocker.patch.object(workflow_context.vellum_client.events, "create", side_effect=slow_events_create)

    # WHEN we emit the workflow event
    emitter.emit_event(workflow_initiated_event)

    # AND we call join() and measure how long it takes
    join_start_time = time.time()
    emitter.join()
    join_duration = time.time() - join_start_time

    # THEN join() should return before the HTTP request completes
    assert join_duration < 1

    # AND the HTTP request should have been called exactly once
    assert mock_create.call_count == 1
