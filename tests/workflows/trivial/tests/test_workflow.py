from tests.workflows.trivial.workflow import TrivialWorkflow


def test_run_workflow__happy_path():
    workflow = TrivialWorkflow()
    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled"


def test_stream_workflow__happy_path():
    workflow = TrivialWorkflow()
    stream = workflow.stream()
    events = list(stream)

    assert len(events) == 2

    assert events[0].name == "workflow.execution.initiated"

    assert events[1].name == "workflow.execution.fulfilled"

    for event in events:
        assert event.span_id == stream.span_id
