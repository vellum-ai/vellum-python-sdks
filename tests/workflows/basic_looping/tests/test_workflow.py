from vellum.workflows.nodes.mocks import MockNodeExecution

from tests.workflows.basic_looping.workflow import BasicLoopingWorkflow, StartNode


def test_workflow__happy_path():
    # GIVEN a workflow that defines a loop
    workflow = BasicLoopingWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN we should get the expected output
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.final_value == 13
    assert terminal_event.outputs.node_execution_count == 5


def test_workflow__happy_path_with_mocks():
    # GIVEN a workflow that defines a loop
    workflow = BasicLoopingWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run(
        node_output_mocks=[
            MockNodeExecution(
                when_condition=StartNode.Execution.count.equals(0),
                then_outputs=StartNode.Outputs(final_value=5),
            ),
            MockNodeExecution(
                when_condition=StartNode.Execution.count.equals(1),
                then_outputs=StartNode.Outputs(final_value=15),
            ),
        ]
    )

    # THEN we should get the expected output
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.final_value == 15
    assert terminal_event.outputs.node_execution_count == 2
