from datetime import datetime, timezone
import time
from unittest import mock
from uuid import UUID

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.events.workflow import WorkflowExecutionInitiatedBody, WorkflowExecutionInitiatedEvent
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class TestInputs(BaseInputs):
    foo: str = "bar"


class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
    pass


def test_vellum_emitter_debounce_batches_events():
    """
    Test that VellumEmitter batches multiple events when they arrive within debounce window.
    """
    emitter = VellumEmitter(debounce_timeout=0.05)

    mock_context = mock.MagicMock()
    mock_client = mock.MagicMock()
    mock_context.vellum_client = mock_client
    emitter._context = mock_context

    event1: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test1"),
        ),
    )
    event2: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174002"),
        timestamp=datetime(2024, 1, 1, 12, 0, 1, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174002"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174002"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test2"),
        ),
    )

    emitter.emit_event(event1)
    emitter.emit_event(event2)

    time.sleep(0.15)

    assert mock_client.events.create.call_count == 1
    call_args = mock_client.events.create.call_args
    assert len(call_args.kwargs["request"]) == 2
    assert call_args.kwargs["request"][0] == event1
    assert call_args.kwargs["request"][1] == event2


def test_vellum_emitter_debounce_single_event():
    """
    Test that VellumEmitter sends single event when only one event is queued.
    """
    emitter = VellumEmitter(debounce_timeout=0.05)

    mock_context = mock.MagicMock()
    mock_client = mock.MagicMock()
    mock_context.vellum_client = mock_client
    emitter._context = mock_context

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174003"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174003"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174003"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test"),
        ),
    )

    emitter.emit_event(event)

    time.sleep(0.1)

    assert mock_client.events.create.call_count == 1
    call_args = mock_client.events.create.call_args
    assert call_args.kwargs["request"] == [event]


def test_vellum_emitter_debounce_timer_reset():
    """
    Test that debounce timer resets when new events arrive.
    """
    emitter = VellumEmitter(debounce_timeout=0.5)

    mock_context = mock.MagicMock()
    mock_client = mock.MagicMock()
    mock_context.vellum_client = mock_client
    emitter._context = mock_context

    event1: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174004"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174004"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174004"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test1"),
        ),
    )
    event2: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174005"),
        timestamp=datetime(2024, 1, 1, 12, 0, 1, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174005"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174005"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test2"),
        ),
    )

    emitter.emit_event(event1)

    time.sleep(0.1)

    emitter.emit_event(event2)

    time.sleep(0.1)

    assert mock_client.events.create.call_count == 0

    time.sleep(0.4)
    assert mock_client.events.create.call_count == 1
    call_args = mock_client.events.create.call_args
    assert len(call_args.kwargs["request"]) == 2


def test_vellum_emitter_debounce_no_context():
    """
    Test that VellumEmitter handles missing context gracefully.
    """
    emitter = VellumEmitter(debounce_timeout=0.05)

    event: WorkflowExecutionInitiatedEvent = WorkflowExecutionInitiatedEvent(
        id=UUID("123e4567-e89b-12d3-a456-426614174006"),
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        trace_id=UUID("123e4567-e89b-12d3-a456-426614174006"),
        span_id=UUID("123e4567-e89b-12d3-a456-426614174006"),
        body=WorkflowExecutionInitiatedBody(
            workflow_definition=TestWorkflow,
            inputs=TestInputs(foo="test"),
        ),
    )

    emitter.emit_event(event)

    time.sleep(0.1)

    assert len(emitter._event_queue) == 0


def test_vellum_emitter_debounce_disallowed_events():
    """
    Test that disallowed events are not queued.
    """
    emitter = VellumEmitter(debounce_timeout=0.05)

    mock_context = mock.MagicMock()
    mock_client = mock.MagicMock()
    mock_context.vellum_client = mock_client
    emitter._context = mock_context

    event = mock.MagicMock()
    event.name = "workflow.execution.streaming"

    emitter.emit_event(event)

    time.sleep(0.1)

    assert mock_client.events.create.call_count == 0
    assert len(emitter._event_queue) == 0
