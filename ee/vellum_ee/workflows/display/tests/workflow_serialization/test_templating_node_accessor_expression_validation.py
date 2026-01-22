from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__templating_node_with_accessor_expression():
    """
    Tests that serialization returns an error when a Templating Node uses an accessor
    expression from a Prompt Node JSON output. The error should guide users to access
    the JSON key within the template itself instead of using accessor expressions.
    """

    # GIVEN a workflow module with a Templating Node that uses an accessor expression
    # from a Prompt Node JSON output (e.g., PromptNode.Outputs.json.response)
    module = "tests.workflows.test_templating_node_accessor_expression_validation"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should contain an error about accessor expressions
    assert len(result.errors) > 0

    # AND the error message should guide users to access the JSON key within the template
    error_messages = [error.message for error in result.errors]
    assert any(
        "Accessor expressions are not supported for Templating Node inputs" in msg
        and "access the key within the template" in msg
        for msg in error_messages
    ), f"Expected accessor expression error in error messages, got: {error_messages}"
