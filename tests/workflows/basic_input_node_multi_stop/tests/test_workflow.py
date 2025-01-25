from tests.workflows.basic_input_node_multi_stop.workflow import (
    BasicInputNodeWorkflow,
    Inputs,
    MiddleNode,
    MiddleNode2,
    State,
)


def test_workflow__happy_path_multi_stop():
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
    terminal2_event = workflow.run(
        external_inputs={
            MiddleNode.ExternalInputs.message: "sunny",
        },
    )

    assert terminal2_event.name == "workflow.execution.paused"
    external_inputs = list(terminal2_event.external_inputs)
    assert MiddleNode2.ExternalInputs.message == external_inputs[0]
    assert len(external_inputs) == 1

    # WHEN we resume the workflow
    final_terminal_event = workflow.run(
        external_inputs={
            MiddleNode2.ExternalInputs.message: "rain",
        },
    )

    # THEN we should get workflow in FULFILLED state
    assert final_terminal_event.name == "workflow.execution.fulfilled"
    assert final_terminal_event.outputs.final_value == "hello sunny rain world"


def test_workflow__happy_path_stream_multi_stop():
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

    # AND we should end with another PAUSED state
    last_event = events[-1]
    assert last_event.name == "workflow.execution.paused"

    # WHEN we resume the workflow
    stream2 = workflow.stream(
        external_inputs={
            MiddleNode2.ExternalInputs.message: "rain",
        },
    )
    events = list(stream2)

    # THEN we should have started with a RESUMED state
    assert events[0].name == "workflow.execution.resumed"

    # AND we should end with a FULFILLED state
    final_event = events[-1]
    assert final_event.name == "workflow.execution.fulfilled"
    assert final_event.outputs.final_value == "hello sunny rain world"
