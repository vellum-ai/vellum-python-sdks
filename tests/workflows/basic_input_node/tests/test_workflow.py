from tests.workflows.basic_input_node.workflow import BasicInputNodeWorkflow, Inputs, MiddleNode, State


def test_workflow__happy_path():
    """
    Runs the non-streamed execution of a workflow with an Input Node.
    """

    # GIVEN a workflow that uses an Input Node
    workflow = BasicInputNodeWorkflow()

    # WHEN we run the workflow with initial inputs and state
    terminal_event = workflow.run(
        inputs=Inputs(input_value="hello"),
        state=State(state_value="world"),
    )

    # THEN we should get workflow in PAUSED state
    assert terminal_event.name == "workflow.execution.paused"
    external_inputs = list(terminal_event.external_inputs)
    assert MiddleNode.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow
    final_terminal_event = workflow.run(
        external_inputs={
            MiddleNode.ExternalInputs.message: "sunny",
        },
    )

    # THEN we should get workflow in FULFILLED state
    assert final_terminal_event.name == "workflow.execution.fulfilled"
    assert final_terminal_event.outputs.final_value == "hello sunny world"

    # AND the workflow execution should have the same span id
    assert final_terminal_event.span_id == terminal_event.span_id


def test_workflow__happy_path_stream():
    """
    Runs the streaming execution of a workflow with an Input Node.
    """

    # GIVEN a workflow that uses an Input Node
    workflow = BasicInputNodeWorkflow()

    # WHEN we run the workflow with initial inputs and state
    terminal_event = workflow.run(
        inputs=Inputs(input_value="hello"),
        state=State(state_value="world"),
    )

    # THEN we should get workflow in PAUSED state
    assert terminal_event.name == "workflow.execution.paused"
    external_inputs = list(terminal_event.external_inputs)
    assert MiddleNode.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow
    stream = workflow.stream(
        external_inputs={
            MiddleNode.ExternalInputs.message: "sunny",
        },
    )
    events = list(stream)

    # THEN we should have started with a RESUMED state
    assert events[0].name == "workflow.execution.resumed"

    # AND we should end with a FULFILLED state
    final_event = events[-1]
    assert final_event.name == "workflow.execution.fulfilled"
    assert final_event.outputs.final_value == "hello sunny world"

    # AND the workflow execution should have the same span id
    assert events[0].span_id == terminal_event.span_id
    assert final_event.span_id == terminal_event.span_id
