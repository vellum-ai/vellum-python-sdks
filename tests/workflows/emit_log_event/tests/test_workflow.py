import json
from unittest import mock

from vellum.workflows.emitters.vellum_emitter import VellumEmitter
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.emit_log_event.workflow import EmitLogEventWorkflow, LoggingNode


def test_emit_log_event__happy_path():
    # GIVEN a workflow with a node that emits a log event
    workflow = EmitLogEventWorkflow()

    # WHEN
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # THEN
    node_events = [e for e in events if e.name in ["node.execution.initiated", "node.execution.fulfilled"]]
    assert len(node_events) == 2

    trace_ids = [node_event.trace_id for node_event in node_events]
    assert len(set(trace_ids)) == 1, trace_ids
    expected_trace_id = trace_ids[0]

    span_ids = [node_event.span_id for node_event in node_events]
    assert len(set(span_ids)) == 1, span_ids
    expected_span_id = span_ids[0]

    log_events = [e for e in events if e.name == "node.execution.log"]
    assert len(log_events) == 1

    log_event = log_events[0]
    assert log_event.trace_id == expected_trace_id
    assert log_event.span_id == expected_span_id
    assert log_event.body.severity == "INFO"
    assert log_event.body.message == "Custom log message"
    assert log_event.body.attributes == {"key": "value", "count": 42}
    assert log_event.body.node_definition == LoggingNode


def test_emit_log_event__sent_to_monitoring_api(mock_httpx_transport):
    """Test that NodeExecutionLogEvent is sent to monitoring API via VellumEmitter."""

    # GIVEN a workflow configured with the default VellumEmitter
    emitter = VellumEmitter(debounce_timeout=0.01)
    workflow = EmitLogEventWorkflow(emitters=[emitter])

    # WHEN
    workflow.run()
    workflow.join()

    # THEN we should've emitted a single node log event
    assert mock_httpx_transport.handle_request.call_count >= 1

    all_events = []
    for call_args in mock_httpx_transport.handle_request.call_args_list:
        mocked_request = call_args.args[0]
        if mocked_request.url == "https://api.vellum.ai/monitoring/v1/events":
            events_in_request = json.loads(mocked_request.content)
            all_events.extend(events_in_request)

    node_events = [e for e in all_events if e.get("name") in ["node.execution.initiated", "node.execution.fulfilled"]]
    assert len(node_events) == 2

    node_event_trace_ids = [node_event["trace_id"] for node_event in node_events]
    assert len(set(node_event_trace_ids)) == 1, node_event_trace_ids
    expected_node_event_trace_id = node_event_trace_ids[0]

    node_event_span_ids = [node_event["span_id"] for node_event in node_events]
    assert len(set(node_event_span_ids)) == 1, node_event_span_ids
    expected_node_event_span_id = node_event_span_ids[0]

    log_events = [e for e in all_events if e.get("name") == "node.execution.log"]
    assert len(log_events) == 1

    log_event = log_events[0]
    assert log_event == {
        "api_version": "2024-10-25",
        "body": {
            "attributes": {"count": 42, "key": "value"},
            "message": "Custom log message",
            "node_definition": {
                "exclude_from_monitoring": False,
                "id": mock.ANY,
                "module": ["tests", "workflows", "emit_log_event", "workflow"],
                "name": "LoggingNode",
            },
            "severity": "INFO",
        },
        "id": mock.ANY,
        "name": "node.execution.log",
        "span_id": expected_node_event_span_id,
        "timestamp": mock.ANY,
        "trace_id": expected_node_event_trace_id,
    }
