from tests.workflows.basic_ports.else_with_no_if.workflow import ElseWithNoIfWorkflow, Inputs


def test_run_workflow():
    workflow = ElseWithNoIfWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))

    base_module = __name__.split(".")[:-2]
    assert terminal_event.name == "workflow.execution.rejected"
    assert (
        terminal_event.error.message
        == f"Class {'.'.join(base_module)}.workflow.ElseWithNoIfNode.Ports must have ports in the following order: on_if, on_elif, on_else"  # noqa E501
    )
