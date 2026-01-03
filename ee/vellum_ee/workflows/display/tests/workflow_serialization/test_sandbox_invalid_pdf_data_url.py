from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__invalid_pdf_data_url():
    """
    Tests that serialization returns an error when sandbox.py has an invalid PDF data URL
    without wrecking the whole serialize process.
    """

    # GIVEN a workflow module with a sandbox.py that has an invalid PDF data URL
    module = "tests.workflows.test_sandbox_invalid_pdf_data_url"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should still contain a valid exec_config
    assert result.exec_config is not None
    assert isinstance(result.exec_config, dict)

    # AND the result should contain an error about the invalid PDF data URL
    assert len(result.errors) > 0

    # AND the error message should mention the invalid base64 encoding in PDF data URL
    error_messages = [error.message for error in result.errors]
    assert any(
        "Invalid base64 encoding in PDF data URL" in msg for msg in error_messages
    ), f"Expected 'Invalid base64 encoding in PDF data URL' in error messages, got: {error_messages}"
