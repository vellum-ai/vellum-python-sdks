from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__invalid_mocks_reference():
    """
    Tests that serialization returns an error when sandbox.py has an invalid Mocks reference on a node.
    """

    # GIVEN a workflow module with a sandbox.py that references CodeExecution.Mocks.Outputs
    # which doesn't exist - nodes don't have a Mocks nested class
    module = "tests.workflows.test_sandbox_invalid_mocks_reference"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about the invalid attribute access
    assert len(result.errors) > 0

    # AND the error should be an AttributeError from trying to access a non-existent attribute
    error_messages = [error.message for error in result.errors]
    assert any(
        "__annotations__" in msg or "has no attribute" in msg for msg in error_messages
    ), f"Expected attribute error in error messages, got: {error_messages}"


def test_serialize_module__invalid_runner_kwarg():
    """
    Tests that serialization returns an error when sandbox.py uses an invalid kwarg on WorkflowSandboxRunner.
    """

    # GIVEN a workflow module with a sandbox.py that uses 'scenarios' kwarg instead of 'dataset'
    module = "tests.workflows.test_sandbox_invalid_runner_kwarg"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about the invalid keyword argument
    assert len(result.errors) > 0

    # AND the error message should mention the unexpected keyword argument 'scenarios'
    error_messages = [error.message for error in result.errors]
    assert any(
        "scenarios" in msg for msg in error_messages
    ), f"Expected 'scenarios' in error messages, got: {error_messages}"
