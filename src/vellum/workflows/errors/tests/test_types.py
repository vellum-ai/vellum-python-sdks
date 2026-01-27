from typing import Any, Dict, Optional

from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode, workflow_error_to_vellum_error


def test_workflow_error_to_vellum_error__preserves_raw_data():
    """
    Tests that raw_data is preserved when converting WorkflowError to VellumError.
    """
    # GIVEN a WorkflowError with raw_data containing integration details
    raw_data: Dict[str, Optional[Any]] = {
        "integration": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "provider": "COMPOSIO",
            "name": "GITHUB",
        }
    }
    workflow_error = WorkflowError(
        message="Integration credentials unavailable",
        code=WorkflowErrorCode.INTEGRATION_CREDENTIALS_UNAVAILABLE,
        raw_data=raw_data,
    )

    # WHEN we convert to VellumError
    vellum_error = workflow_error_to_vellum_error(workflow_error)

    # THEN the raw_data should be preserved
    assert vellum_error.raw_data == raw_data

    # AND the integration details should be accessible
    raw_data_from_error = vellum_error.raw_data
    assert raw_data_from_error is not None
    integration = raw_data_from_error.get("integration")
    assert isinstance(integration, dict)
    assert integration["name"] == "GITHUB"
    assert integration["provider"] == "COMPOSIO"


def test_workflow_error_to_vellum_error__handles_none_raw_data():
    """
    Tests that None raw_data is handled correctly when converting WorkflowError to VellumError.
    """
    # GIVEN a WorkflowError with no raw_data
    workflow_error = WorkflowError(
        message="Some error",
        code=WorkflowErrorCode.INTERNAL_ERROR,
        raw_data=None,
    )

    # WHEN we convert to VellumError
    vellum_error = workflow_error_to_vellum_error(workflow_error)

    # THEN the raw_data should be None
    assert vellum_error.raw_data is None
