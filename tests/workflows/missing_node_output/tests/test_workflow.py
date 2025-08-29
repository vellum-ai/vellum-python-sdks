from tests.workflows.missing_node_output.workflow import MissingNodeOutputWorkflow


def test_workflow__happy_path():
    # GIVEN a workflow setup to try to resolve an unresolved node output
    workflow = MissingNodeOutputWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should expect the workflow to succeed with the expected output
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {"final_value": "hello "}
