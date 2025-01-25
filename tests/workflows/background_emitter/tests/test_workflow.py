import time

from tests.workflows.background_emitter.workflow import BackgroundEmitterWorkflow, ExpensiveEmitter


def test_workflow__happy_path(mocker):
    """
    Test that a Workflow with an expensive data emitter completes without waiting
    for the emitter to complete.
    """

    # MOCK the emitter's emit_event
    emitter = ExpensiveEmitter()
    mock_emit_event = mocker.patch.object(emitter, "emit_event", side_effect=emitter.emit_event)

    # GIVEN a workflow with an expensive data emitter
    workflow = BackgroundEmitterWorkflow()
    workflow.emitters = [emitter]

    # WHEN the workflow is run
    start_time = time.time()
    terminal_event = workflow.run()
    end_time = time.time()

    # THEN the workflow nodes completed without blocking on the emitter
    assert terminal_event.name == "workflow.execution.fulfilled"
    # TODO: Remove this once we've resolved `terminal_event.outputs.final_value`
    # from `OutputReference[T]` to `T`.
    # https://app.shortcut.com/vellum/story/4936
    assert terminal_event.outputs.final_value < emitter.delay  # type: ignore[operator]

    # AND the workflow itself completed without blocking on the emitter
    assert end_time - start_time < emitter.delay

    # AND the emitter was called at least once
    assert mock_emit_event.call_count > 0, "Expected emitter.emit_event to be called"
