from tests.workflows.multi_branch_merge_loop.workflow import MultiBranchMergeLoopWorkflow


def test_workflow__happy_path():
    # GIVEN a workflow with multiple branches and a merge loop
    workflow = MultiBranchMergeLoopWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs == {
        "final_value": "hello",
        "final_counter": 2,
    }
