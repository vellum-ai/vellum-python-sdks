from datetime import datetime, timedelta

from tests.workflows.max_concurrent_threads.workflow import MaxConcurrentThreadsExample


def test_run_workflow_limit_concurrency__happy_path():
    # GIVEN a workflow that references a Map example with a max concurrency of 1
    workflow = MaxConcurrentThreadsExample()

    # WHEN the workflow is run
    datetime_start = datetime.now()
    terminal_event = workflow.run(max_concurrency=1)

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the runtime indicates that the workflow ran in serial
    assert terminal_event.timestamp - datetime_start > timedelta(seconds=0.3)


def test_run_workflow__happy_path():
    # GIVEN a workflow that references a Map example with no max concurrency
    workflow = MaxConcurrentThreadsExample()

    # WHEN the workflow is run
    datetime_start = datetime.now()
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the runtime indicates that the workflow ran in parallel
    assert terminal_event.timestamp - datetime_start < timedelta(seconds=0.3)


def test_stream_workflow_limit_concurrency__happy_path():
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


def test_stream_workflow__happy_path():
    # GIVEN a workflow that references a Map example with no max concurrency
    workflow = MaxConcurrentThreadsExample()

    # WHEN the workflow is run
    stream = workflow.stream()
    events = list(stream)

    # THEN the workflow should complete successfully
    first_event = events[0]
    last_event = events[-1]
    assert first_event.name == "workflow.execution.initiated", first_event
    assert last_event.name == "workflow.execution.fulfilled", last_event

    # AND the runtime indicates that the workflow ran in parallel
    assert last_event.timestamp - first_event.timestamp < timedelta(seconds=0.3)
