"""
Test for APO-1936: Conditional nodes internal server error when doing string greater than or equal comparisons.

This test reproduces the error by running a workflow with a conditional node that compares
a string field to a float value.
"""

from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.string_comparison_error.workflow import Inputs, StringComparisonErrorWorkflow


def test_string_comparison_error__string_to_float_comparison():
    """
    Test that reproduces the internal server error when doing string to float comparisons.
    This should raise a user-facing InvalidExpressionException instead of allowing the comparison.

    Reproduces: https://linear.app/vellum/issue/APO-1936
    """

    # GIVEN a workflow with a conditional node that compares a string to a float
    workflow = StringComparisonErrorWorkflow()

    # WHEN we run the workflow with a string field and float value
    terminal_event = workflow.run(inputs=Inputs(field="hello", value=42.0))

    # THEN the workflow should reject with a user-facing error
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS

    assert "Cannot compare 'str' with 'float'" in terminal_event.error.message
