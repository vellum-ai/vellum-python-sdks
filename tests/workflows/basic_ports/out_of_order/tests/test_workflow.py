from tests.workflows.basic_ports.out_of_order.workflow import Inputs, OutOfOrderWorkflow


def test_run_workflow():
    workflow = OutOfOrderWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))

    base_module = __name__.split(".")[:-2]
    assert terminal_event.name == "workflow.execution.rejected"
    assert (
        terminal_event.error.message
        == f"Class {'.'.join(base_module)}.workflow.OutOfOrderNode.Ports must have ports in the following order: on_if, on_elif, on_else"  # noqa E501
    )
