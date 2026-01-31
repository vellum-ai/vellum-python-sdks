from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.custom_node_uncaught_exception.workflow import CustomNodeUncaughtExceptionWorkflow


def test_run_workflow__uncaught_exception_has_stacktrace():
    """
    Tests that when a custom node throws an uncaught exception (like AttributeError),
    the workflow rejection event includes a meaningful stack trace.

    This is the scenario from Linear ticket APO-2674 where custom node exceptions
    were missing stack traces in error output.
    """
    # GIVEN a workflow with a custom node that throws an uncaught exception
    workflow = CustomNodeUncaughtExceptionWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete with a rejection event
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the error should indicate a node execution error
    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION
    assert (
        "AttributeError" in terminal_event.error.message
        or "'str' object has no attribute 'get'" in terminal_event.error.message
    )

    # AND the stacktrace should contain meaningful stack trace information
    assert terminal_event.body.stacktrace is not None, "Stacktrace should not be None"
    assert "AttributeError" in terminal_event.body.stacktrace, "Stacktrace should contain the exception type"
    assert (
        "'str' object has no attribute 'get'" in terminal_event.body.stacktrace
    ), "Stacktrace should contain the error message"
    assert "workflow.py" in terminal_event.body.stacktrace, "Stacktrace should contain the file name"
    assert "in run" in terminal_event.body.stacktrace, "Stacktrace should contain the method name"


def test_stream_workflow__node_rejected_event_has_stacktrace():
    """
    Tests that when streaming a workflow with a custom node that throws an uncaught exception,
    the node.execution.rejected event includes a meaningful stack trace.
    """
    # GIVEN a workflow with a custom node that throws an uncaught exception
    workflow = CustomNodeUncaughtExceptionWorkflow()

    # WHEN the workflow is streamed
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # THEN we should have events
    assert len(events) > 0, "No events were emitted"

    # AND the last event should be workflow.execution.rejected
    workflow_rejected_event = events[-1]
    assert workflow_rejected_event.name == "workflow.execution.rejected"

    # AND there should be a node.execution.rejected event
    node_rejected_events = [e for e in events if e.name == "node.execution.rejected"]
    assert (
        len(node_rejected_events) == 1
    ), f"Expected exactly 1 node.execution.rejected event, got {len(node_rejected_events)}"

    node_rejected_event = node_rejected_events[0]

    # AND the node rejected event should have a stacktrace
    assert node_rejected_event.body.stacktrace is not None, "Node rejected event stacktrace should not be None"
    assert "AttributeError" in node_rejected_event.body.stacktrace, "Node stacktrace should contain the exception type"
    assert (
        "'str' object has no attribute 'get'" in node_rejected_event.body.stacktrace
    ), "Node stacktrace should contain the error message"
    assert "workflow.py" in node_rejected_event.body.stacktrace, "Node stacktrace should contain the file name"
    assert "in run" in node_rejected_event.body.stacktrace, "Node stacktrace should contain the method name"
