from vellum.workflows.nodes.mocks import mock_node

from tests.workflows.nested_node_mocks.workflow import NestedNodeMockWorkflow, NodeToMock


def test_run_workflow__happy_path():
    # GIVEN a workflow that contains a MapNode that contains the actual node we want to mock
    workflow = NestedNodeMockWorkflow()

    with mock_node(NodeToMock) as mocked_node:
        mocked_node.side_effect = lambda inputs: (
            NodeToMock.Outputs(result="date")
            if inputs.index == 0
            else NodeToMock.Outputs(result="eggplant") if inputs.index == 1 else NodeToMock.Outputs(result="fig")
        )

        # WHEN the workflow is run with nested mocks
        terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the mocked items
    assert terminal_event.outputs.final_value == ["date", "eggplant", "fig"]
