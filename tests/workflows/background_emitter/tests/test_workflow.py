import time

from tests.workflows.background_emitter.workflow import BackgroundEmitterWorkflow, ExpensiveEmitter


def test_workflow__happy_path(mocker):
    """
    Test that a Workflow with an expensive data emitter completes without waiting
    for the emitter to complete.
    """

    # MOCK the emit function called by the emitter
    mock_emit = mocker.patch.object(ExpensiveEmitter, "_emit")

    # GIVEN a workflow with an expensive data emitter
    workflow = BackgroundEmitterWorkflow()

    # WHEN the workflow is run
    start_time = time.time()
    terminal_event = workflow.run()
    end_time = time.time()

    # THEN the workflow nodes completed without blocking on the emitter
    assert terminal_event.name == "workflow.execution.fulfilled"
    # TODO: Remove this once we've resolved `terminal_event.outputs.final_value`
    # from `OutputReference[T]` to `T`.
    # https://app.shortcut.com/vellum/story/4936
    assert terminal_event.outputs.final_value < ExpensiveEmitter.delay  # type: ignore[operator]

    # AND the workflow itself completed without blocking on the emitter
    assert end_time - start_time < ExpensiveEmitter.delay + 0.05  # Allow 50ms overhead for execution

    # AND the emitter was called at least once
    deadline = time.time() + 2.0
    while mock_emit.call_count == 0 and time.time() < deadline:
        time.sleep(0.01)
    assert mock_emit.call_count > 0, "Emitter was not called"
