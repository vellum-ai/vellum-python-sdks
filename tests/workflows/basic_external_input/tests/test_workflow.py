from tests.workflows.basic_external_input.workflow import BasicInputNodeWorkflow, InputNode


def test_workflow__happy_path_multi_stop():
    """
    Runs the non-streamed execution of a Workflow with a single Nodes defining ExternalInputs.
    """

    # GIVEN a workflow that uses an Input Node
    workflow = BasicInputNodeWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should get workflow in PAUSED state
    assert terminal_event.name == "workflow.execution.paused"
    external_inputs = list(terminal_event.external_inputs)

    assert InputNode.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow
    final_terminal_event = workflow.run(
        external_inputs={
            InputNode.ExternalInputs.message: "sunny",
        },
    )

    # THEN we should get workflow in FULFILLED state
    assert final_terminal_event.name == "workflow.execution.fulfilled"
    assert final_terminal_event.outputs.final_value == "sunny"
