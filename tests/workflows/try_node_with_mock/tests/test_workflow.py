from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode

from tests.workflows.try_node_with_mock.workflow import TryNodeWithMockWorkflow, WrappedNode


def test_run_workflow__mock_wrapped_node_success():
    """
    Tests that mocking a node wrapped in a TryNode adornment returns the mocked output.
    """

    # GIVEN a workflow with a TryNode-wrapped node
    workflow = TryNodeWithMockWorkflow()

    # WHEN we run the workflow with a mock for the wrapped node
    terminal_event = workflow.run(
        node_output_mocks=[
            WrappedNode.Outputs(result="mocked_result"),
        ]
    )

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the mocked value
    assert terminal_event.outputs.final_result == "mocked_result"

    # AND there should be no error
    assert terminal_event.outputs.error is None


def test_run_workflow__mock_wrapped_node_with_error():
    """
    Tests that mocking a node wrapped in a TryNode adornment with an error returns the error.
    """

    # GIVEN a workflow with a TryNode-wrapped node
    workflow = TryNodeWithMockWorkflow()

    # WHEN we run the workflow with a mock that returns an error
    terminal_event = workflow.run(
        node_output_mocks=[
            WrappedNode.Outputs(  # type: ignore[call-arg]
                error=WorkflowError(
                    message="Mocked error",
                    code=WorkflowErrorCode.NODE_EXECUTION,
                )
            ),
        ]
    )

    # THEN the workflow should complete successfully (TryNode catches the error)
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the error output should match the mocked error
    assert terminal_event.outputs.error == WorkflowError(
        message="Mocked error",
        code=WorkflowErrorCode.NODE_EXECUTION,
    )
