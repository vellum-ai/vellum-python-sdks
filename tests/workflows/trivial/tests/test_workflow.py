from vellum.workflows.events.workflow import WorkflowEventStreamWrapper

from tests.workflows.trivial.workflow import TrivialWorkflow


def test_run_workflow__happy_path():
    workflow = TrivialWorkflow()
    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled"


def test_stream_workflow__happy_path():
    workflow = TrivialWorkflow()
    events = list(workflow.stream())

    assert len(events) == 5

    assert events[0].name == "workflow.execution.initiated"

    assert events[-1].name == "workflow.execution.fulfilled"


def test_stream_workflow__span_id_property():
    workflow = TrivialWorkflow()
    stream = workflow.stream()

    assert isinstance(stream, WorkflowEventStreamWrapper)

    span_id = stream.span_id
    assert span_id is not None

    first_event = next(stream)
    assert span_id == first_event.span_id

    remaining_events = list(stream)
    all_events = [first_event] + remaining_events

    assert len(all_events) >= 2
    assert all_events[0].name == "workflow.execution.initiated"
    assert all_events[-1].name == "workflow.execution.fulfilled"

    workflow_events = [event for event in all_events if event.name.startswith("workflow.")]
    for event in workflow_events:
        assert event.span_id == span_id
