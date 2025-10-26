from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.string_comparison_error.workflow import Inputs, StringComparisonErrorWorkflow


def test_string_comparison_error__string_to_float_comparison_with_non_numeric_string():
    """
    Test that non-numeric strings still raise an error when compared to floats.
    """

    # GIVEN a workflow with a conditional node that compares a string to a float
    workflow = StringComparisonErrorWorkflow()

    # WHEN we run the workflow with a non-numeric string field and float value
    terminal_event = workflow.run(inputs=Inputs(field="hello", value=42.0))

    # THEN the workflow should reject with a user-facing error
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert "'>=' not supported between instances of 'str' and 'float'" in terminal_event.error.message


def test_string_comparison_error__numeric_string_to_float_comparison():
    """
    Test that numeric strings are successfully parsed and compared to floats.
    """

    # GIVEN a workflow with a conditional node that compares a string to a float
    workflow = StringComparisonErrorWorkflow()

    # WHEN we run the workflow with a numeric string field that is greater than the value
    terminal_event = workflow.run(inputs=Inputs(field="50.5", value=42.0))

    # THEN the workflow should succeed (condition evaluates to True, only ConditionalNode runs)
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs.final_result == "if_branch"

    # WHEN we run the workflow with a numeric string field that is less than the value
    terminal_event = workflow.run(inputs=Inputs(field="30", value=42.0))

    # THEN the workflow should succeed (condition evaluates to False, both nodes run)
    assert terminal_event.name == "workflow.execution.fulfilled"
