from unittest import mock

from vellum import CodeExecutorResponse, NumberVellumValue
from vellum.workflows.events.node import NodeExecutionLogBody, NodeExecutionLogEvent
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_code_execution_node.try_workflow import TrySimpleCodeExecutionWorkflow
from tests.workflows.basic_code_execution_node.workflow import (
    SimpleCodeExecutionNode,
    SimpleCodeExecutionWithFilepathWorkflow,
)


def test_run_workflow__happy_path(vellum_client):
    # GIVEN a workflow that references a Code Execution example
    workflow = SimpleCodeExecutionWithFilepathWorkflow()

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=0),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is run
    final_event = workflow.run()

    # THEN the workflow should complete successfully
    assert final_event.name == "workflow.execution.fulfilled", final_event

    # AND the output should match the mapped items
    assert final_event.outputs == {"result": 0, "log": "hello"}


def test_run_workflow__try_wrapped(vellum_client):
    # GIVEN a workflow that references a Code Execution example
    workflow = TrySimpleCodeExecutionWorkflow()

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=0),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is run
    final_event = workflow.run()

    # THEN the workflow should complete successfully
    assert final_event.name == "workflow.execution.fulfilled", final_event

    # AND the output should match the mapped items
    assert final_event.outputs == {"result": 0, "log": "hello"}


def test_run_workflow__emits_log_event(vellum_client):
    # GIVEN a workflow that references a Code Execution example
    workflow = SimpleCodeExecutionWithFilepathWorkflow()

    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=0),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN the workflow is streamed
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # THEN we should emit an event for the log output
    node_events = [e for e in events if e.name in ["node.execution.initiated", "node.execution.fulfilled"]]
    expected_trace_id = node_events[0].trace_id
    expected_span_id = node_events[0].span_id

    # AND a log event should have been emitted with the code execution log
    log_events = [e for e in events if e.name == "node.execution.log"]
    assert log_events == [
        NodeExecutionLogEvent.model_construct(
            id=mock.ANY,
            timestamp=mock.ANY,
            api_version="2024-10-25",
            trace_id=expected_trace_id,
            span_id=expected_span_id,
            parent=None,
            links=None,
            body=NodeExecutionLogBody(
                node_definition=SimpleCodeExecutionNode,
                attributes=None,
                severity="INFO",
                message="hello",
            ),
        )
    ]
