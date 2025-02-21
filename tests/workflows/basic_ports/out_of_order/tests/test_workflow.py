from tests.workflows.basic_ports.out_of_order.workflow import Inputs, OutOfOrderWorkflow


def test_run_workflow():
    workflow = OutOfOrderWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.message == "Port conditions must be in the following order: on_if, on_elif, on_else"
