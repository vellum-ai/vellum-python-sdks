from vellum.workflows.state.store import EmptyStore

from tests.workflows.empty_store.workflow import WorkflowWithEmptyStore


def test_run_workflow__happy_path():
    # GIVEN a trivial workflow with access to a pass through store
    workflow = WorkflowWithEmptyStore(
        store=EmptyStore(),
    )

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow is executed and the store is passed through
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND no events or state snapshots are recorded
    assert list(workflow._store.events) == []
    assert list(workflow._store.state_snapshots) == []
