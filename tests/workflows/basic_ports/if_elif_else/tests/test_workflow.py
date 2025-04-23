from tests.workflows.basic_ports.if_elif_else.workflow import IfElifElseWorkflow, Inputs


def test_run_workflow():
    workflow = IfElifElseWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))

    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {"value": "foo"}
