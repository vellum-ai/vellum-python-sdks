from tests.workflows.nested_node_mocks.workflow import NestedNodeMockWorkflow, NodeToMock


def test_run_workflow__happy_path():
    # GIVEN a workflow that contains a MapNode that contains the actual node we want to mock
    workflow = NestedNodeMockWorkflow()

    # WHEN the workflow is run with nested mocks
    terminal_event = workflow.run(
        node_output_mocks=[
            NodeToMock.Outputs(result="date"),
            NodeToMock.Outputs(result="eggplant"),
            NodeToMock.Outputs(result="fig"),
        ]
    )

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the mocked items
    assert terminal_event.outputs.final_value == ["date", "eggplant", "fig"]
