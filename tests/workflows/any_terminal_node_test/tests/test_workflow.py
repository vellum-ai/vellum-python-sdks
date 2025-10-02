from tests.workflows.any_terminal_node_test.workflow import AnyTerminalNodeWorkflow, Inputs


def test_any_terminal_node_accepts_string_descriptor():
    """
    Tests that a terminal node with Any output type accepts string descriptors.
    """
    workflow = AnyTerminalNodeWorkflow()

    terminal_event = workflow.run(inputs=Inputs(string_input="test string"))

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs == {"value": "test string"}
