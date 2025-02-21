from tests.workflows.basic_ports.else_with_no_if.workflow import ElseWithNoIfWorkflow, Inputs


def test_run_workflow():
    workflow = ElseWithNoIfWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))
    assert terminal_event.name == "workflow.execution.rejected"
    base_module = __name__.split(".")[:-2]
    assert (
        terminal_event.error.message
        == f"Class {'.'.join(base_module)}.workflow.ElseWithNoIfNode.Ports containing on_elif or on_else port conditions must have at least one on_if condition"  # noqa E501
    )
