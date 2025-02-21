from tests.workflows.basic_ports.multiple_if_with_elif.workflow import Inputs, MultipleIfWithElifWorkflow


def test_run_workflow():
    workflow = MultipleIfWithElifWorkflow()
    terminal_event = workflow.run(inputs=Inputs(value="foo"))
    assert terminal_event.name == "workflow.execution.rejected"
    base_module = __name__.split(".")[:-2]
    assert (
        terminal_event.error.message
        == f"Class {'.'.join(base_module)}.workflow.MultipleIfWithElifNode.Ports containing on_elif ports must have exactly one on_if condition"  # noqa E501
    )
