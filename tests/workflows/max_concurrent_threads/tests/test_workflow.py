from datetime import timedelta

from tests.workflows.max_concurrent_threads.workflow import MaxConcurrentThreadsExample


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a Map example with a max concurrency of 1
    workflow = MaxConcurrentThreadsExample()

    # WHEN the workflow is run
    stream = workflow.stream(max_concurrency=1)
    events = list(stream)

    # THEN the workflow should complete successfully
    first_event = events[0]
    last_event = events[-1]
    assert first_event.name == "workflow.execution.initiated", first_event
    assert last_event.name == "workflow.execution.fulfilled", last_event

    # AND the runtime indicates that the workflow ran in serial
    assert last_event.timestamp - first_event.timestamp > timedelta(seconds=0.3)
