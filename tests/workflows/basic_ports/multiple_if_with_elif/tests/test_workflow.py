from tests.workflows.basic_ports.multiple_if_with_elif.workflow import Inputs, MultipleIfWithElifWorkflow


def test_run_workflow():
    workflow = MultipleIfWithElifWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))

    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {"value": "foo"}
