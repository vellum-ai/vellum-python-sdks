from tests.workflows.basic_ports.elif_with_no_if.workflow import ElifWithNoIfWorkflow, Inputs


def test_run_workflow():
    workflow = ElifWithNoIfWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.message == "Port conditions must be in the following order: on_if, on_elif, on_else"
