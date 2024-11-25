from threading import Event as ThreadingEvent, Thread
import time

from tests.workflows.basic_cancellable_workflow.workflow import BasicCancellableWorkflow
from vellum.workflows.errors.types import VellumErrorCode


def test_workflow__cancel_run():
    """
    Test that we can cancel a run of a long running workflow.
    """

    # GIVEN a workflow that is long running
    workflow = BasicCancellableWorkflow()

    # AND we have a cancel signal
    cancel_signal = ThreadingEvent()

    # AND some other thread triggers the cancel signal
    def cancel_target():
        time.sleep(0.01)
        cancel_signal.set()

    cancel_thread = Thread(target=cancel_target)
    cancel_thread.start()

    # WHEN we run the workflow
    terminal_event = workflow.run(cancel_signal=cancel_signal)

    # THEN we should get the expected rejection
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.message == "Workflow run cancelled"
    assert terminal_event.error.code == VellumErrorCode.WORKFLOW_CANCELLED


def test_workflow__cancel_stream():
    """
    Test that we can cancel a streaming run of a long running workflow.
    """

    # GIVEN a workflow that is long running
    workflow = BasicCancellableWorkflow()

    # AND we have a cancel signal
    cancel_signal = ThreadingEvent()

    # AND some other thread triggers the cancel signal
    def cancel_target():
        time.sleep(0.01)
        cancel_signal.set()

    cancel_thread = Thread(target=cancel_target)
    cancel_thread.start()

    # WHEN we run the workflow
    result = workflow.stream(cancel_signal=cancel_signal)

    # THEN we should get the expected initiated and rejected events
    events = list(result)
    assert events[0].name == "workflow.execution.initiated"
    assert events[-1].name == "workflow.execution.rejected"
    assert events[-1].error.message == "Workflow run cancelled"
    assert events[-1].error.code == VellumErrorCode.WORKFLOW_CANCELLED