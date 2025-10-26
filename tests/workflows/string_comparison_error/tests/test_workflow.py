from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.string_comparison_error.workflow import Inputs, StringComparisonErrorWorkflow


def test_string_comparison_error__string_to_float_comparison():
    """
    Test that reproduces the internal server error when doing string to float comparisons.
    This should raise a user-facing InvalidExpressionException instead of allowing the comparison.
    """

    # GIVEN a workflow with a conditional node that compares a string to a float
    workflow = StringComparisonErrorWorkflow()

    # WHEN we run the workflow with a string field and float value
    terminal_event = workflow.run(inputs=Inputs(field="hello", value=42.0))

    # THEN the workflow should reject with a user-facing error
    assert terminal_event.name == "workflow.execution.rejected"
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert "'>=' not supported between instances of 'str' and 'float'" in terminal_event.error.message
