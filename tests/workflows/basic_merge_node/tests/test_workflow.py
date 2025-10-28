from vellum.workflows.constants import undefined

from tests.workflows.basic_merge_node.await_all_workflow import AwaitAllFailingWorkflow, AwaitAllPassingWorkflow
from tests.workflows.basic_merge_node.await_any_workflow import AwaitAnyPassingWorkflow


def test_run_workflow__await_all__passing():
    # GIVEN a workflow that passes an await all merge node
    workflow = AwaitAllPassingWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND there should be a final output
    assert terminal_event.outputs == {"value": "output"}


def test_run_workflow__await_all__failing():
    # GIVEN a workflow that fails an await all merge node
    workflow = AwaitAllFailingWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND there should not be a final output
    assert terminal_event.outputs.value is undefined


def test_run_workflow__await_any__passing():
    # GIVEN a workflow that passes an await any merge node
    workflow = AwaitAnyPassingWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND there should be a final output
    assert terminal_event.outputs == {"value": "output"}
