from tests.workflows.no_graph.workflow import BasicNoGraphWorkflow


def test_workflow__happy_path():
    # GIVEN a workflow that has no graph
    workflow = BasicNoGraphWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs == {}
