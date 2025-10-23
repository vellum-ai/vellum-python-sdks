from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.basic_timeout_workflow.workflow import BasicTimeoutWorkflow


def test_workflow__timeout_run():
    """
    Tests that a workflow times out when the timeout is exceeded.
    """

    # GIVEN a workflow that is long running
    workflow = BasicTimeoutWorkflow()

    terminal_event = workflow.run(timeout=0.1)

    # THEN we should get the expected rejection
    assert terminal_event.name == "workflow.execution.rejected"
    assert "timeout" in terminal_event.error.message.lower()
    assert terminal_event.error.code == WorkflowErrorCode.WORKFLOW_TIMEOUT


def test_workflow__timeout_stream():
    """
    Tests that a streaming workflow times out when the timeout is exceeded.
    """

    # GIVEN a workflow that is long running
    workflow = BasicTimeoutWorkflow()

    result = workflow.stream(timeout=0.1, event_filter=root_workflow_event_filter)

    # THEN we should get the expected initiated and rejected events
    events = list(result)
    assert events[0].name == "workflow.execution.initiated"
    assert events[-2].name == "node.execution.rejected"
    assert events[-1].name == "workflow.execution.rejected"
    assert "timeout" in events[-1].error.message.lower()
    assert events[-1].error.code == WorkflowErrorCode.WORKFLOW_TIMEOUT


def test_workflow__timeout_not_exceeded__run():
    """
    Tests that a workflow runs to completion when the timeout is not exceeded.
    """

    # GIVEN a workflow that is long running
    workflow = BasicTimeoutWorkflow()

    terminal_event = workflow.run(timeout=5.0)

    # THEN the workflow should run to completion
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.final_value == "hello world"


def test_workflow__no_timeout__run():
    """
    Tests that a workflow runs to completion when no timeout is specified.
    """

    # GIVEN a workflow that is long running
    workflow = BasicTimeoutWorkflow()

    terminal_event = workflow.run()

    # THEN the workflow should run to completion
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.final_value == "hello world"


def test_workflow__timeout_includes_stacktrace():
    """
    Tests that a workflow timeout includes a stacktrace in the rejected event.
    """

    # GIVEN a workflow that is long running
    workflow = BasicTimeoutWorkflow()

    terminal_event = workflow.run(timeout=0.1)

    # THEN we should get a rejection with a stacktrace
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.WORKFLOW_TIMEOUT

    assert terminal_event.stacktrace is not None
    assert len(terminal_event.stacktrace) > 0
    assert "_run_timeout_thread" in terminal_event.stacktrace
