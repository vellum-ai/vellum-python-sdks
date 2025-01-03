from tests.workflows.basic_generic_node.workflow import BasicGenericNodeWorkflow, Inputs


def test_workflow__happy_path():
    # GIVEN a workflow that just passes through its input to a terminal node
    workflow = BasicGenericNodeWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run(inputs=Inputs(input="hello"))

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event
    assert terminal_event.outputs == {"output": "hello"}
