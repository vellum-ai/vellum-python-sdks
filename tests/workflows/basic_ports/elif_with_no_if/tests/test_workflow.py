from tests.workflows.basic_ports.elif_with_no_if.workflow import ElifWithNoIfWorkflow, Inputs


def test_run_workflow():
    workflow = ElifWithNoIfWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))
    assert terminal_event.name == "workflow.execution.rejected"
    base_module = __name__.split(".")[:-2]
    assert (
        terminal_event.error.message
        == f"Class {'.'.join(base_module)}.workflow.ElifWithNoIfNode.Ports containing on_elif or on_else port conditions must have at least one on_if condition"  # noqa E501
    )
