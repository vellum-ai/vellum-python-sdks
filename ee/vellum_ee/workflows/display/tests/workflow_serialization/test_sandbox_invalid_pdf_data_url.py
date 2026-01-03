from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay


def test_serialize_module__invalid_pdf_data_url():
    """
    Tests that serialization returns an error when sandbox.py has an invalid PDF data URL
    without wrecking the whole serialize process, and that valid dataset rows are still returned.
    """

    # GIVEN a workflow module with a sandbox.py that has one invalid and one valid PDF data URL
    module = "tests.workflows.test_sandbox_invalid_pdf_data_url"

    # WHEN we serialize the module
    result = BaseWorkflowDisplay.serialize_module(module)

    # THEN the result should still contain a valid exec_config
    assert result.exec_config is not None
    assert isinstance(result.exec_config, dict)

    # AND the result should contain exactly one error about the invalid PDF data URL
    assert len(result.errors) == 1
    error_message = result.errors[0].message

    # AND the error message should include the dataset row label
    assert 'Dataset row "Scenario with invalid PDF"' in error_message

    # AND the error message should include the input name
    assert 'input "document"' in error_message

    # AND the error message should mention the invalid base64 encoding
    assert "Invalid base64 encoding in PDF data URL" in error_message

    # AND the result should contain both dataset rows
    assert result.dataset is not None
    assert len(result.dataset) == 2

    # AND the first row should have the valid input (name) serialized but the invalid input (document) skipped
    invalid_row = result.dataset[0]
    assert invalid_row["label"] == "Scenario with invalid PDF"
    assert "document" not in invalid_row["inputs"]
    assert "name" in invalid_row["inputs"]
    assert invalid_row["inputs"]["name"] == "Test User"

    # AND the second row (valid) should have both inputs serialized
    valid_row = result.dataset[1]
    assert valid_row["label"] == "Scenario with valid PDF"
    assert "document" in valid_row["inputs"]
    assert "name" in valid_row["inputs"]
    assert valid_row["inputs"]["name"] == "Another User"
