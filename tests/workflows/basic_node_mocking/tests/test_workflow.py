from tests.workflows.basic_node_mocking.workflow import MockedNodeWorkflow, StartNode


def test_workflow__happy_path():
    # GIVEN a workflow with a node that needs to be mocked to succeed
    workflow = MockedNodeWorkflow()

    # WHEN we run the workflow with a mock defined
    final_event = workflow.run(
        node_output_mocks=[
            StartNode.Outputs(greeting="Hello"),
        ]
    )

    # THEN the workflow should succeed
    assert final_event.name == "workflow.execution.fulfilled", final_event
    assert final_event.outputs.final_value == "Hello, World!"
