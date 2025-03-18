from tests.workflows.await_all_loop_merge_all.workflow import LoopBeforeAwaitAllWorkflow


def test_loop_before_await_all_merge_node_with_fix():
    # GIVEN a workflow with a loop before a merge node with AWAIT_ALL behavior
    workflow = LoopBeforeAwaitAllWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    assert terminal_event.outputs.a_executions == 3
    assert terminal_event.outputs.b_executions == 3
    assert terminal_event.outputs.c_executions == 1
