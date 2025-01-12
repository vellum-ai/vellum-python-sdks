from vellum.workflows.nodes.mocks import mock_node

from tests.workflows.basic_node_mocking.workflow import MockedNodeWorkflow, StartNode


def test_workflow__happy_path():
    # GIVEN a workflow with a node that needs to be mocked to succeed
    workflow = MockedNodeWorkflow()

    # AND we mock the node's output
    with mock_node(StartNode) as mocked_start_node:
        mocked_start_node.outputs = StartNode.Outputs(
            greeting="Hello",
        )

        # WHEN we run the workflow with a mock defined
        final_event = workflow.run()

    # THEN the workflow should succeed
    assert final_event.name == "workflow.execution.fulfilled", final_event
    assert final_event.outputs.final_value == "Hello, World!"
