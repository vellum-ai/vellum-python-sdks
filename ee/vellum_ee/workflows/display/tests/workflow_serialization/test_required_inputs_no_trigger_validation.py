from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__required_inputs_no_trigger_no_values():
    """
    Tests that serialization returns an error when a workflow has required input variables
    but the scenario has no inputs and no trigger.
    """

    # GIVEN a workflow module with required input variables
    # AND a sandbox with a DatasetRow that has no inputs and no trigger
    module = "tests.workflows.test_required_inputs_no_trigger"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about missing required inputs
    assert len(result.errors) > 0, "Expected errors for missing required inputs, got none"

    # AND the error message should mention the missing required input
    error_messages = [error.message for error in result.errors]
    assert any(
        "transcript" in msg.lower() or "required" in msg.lower() for msg in error_messages
    ), f"Expected error about missing required input 'transcript', got: {error_messages}"
