from tests.workflows.basic_ports.multiple_if_else_group.workflow import Inputs, MultipleIfElifElseWorkflow


def test_run_workflow_multiple():
    workflow = MultipleIfElifElseWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))

    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {"value": "foo", "another_value": "foo"}
