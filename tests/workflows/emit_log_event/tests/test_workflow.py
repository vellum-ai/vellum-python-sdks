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
    log_events = [e for e in events if e.name == "node.execution.log"]
    assert len(log_events) == 1

    log_event = log_events[0]
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
        "span_id": mock.ANY,
        "timestamp": mock.ANY,
        "trace_id": mock.ANY,
    }
