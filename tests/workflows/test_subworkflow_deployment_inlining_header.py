from unittest.mock import Mock, patch

from vellum.client.core.api_error import ApiError
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext


def test_resolve_workflow_deployment__adds_always_success_header():
    """
    Test that resolve_workflow_deployment adds X-Vellum-Always-Success header when making pull API calls.
    """
    mock_client = Mock()
    mock_client.workflows.pull.return_value = iter([b"mock zip content"])

    context = WorkflowContext(
        vellum_client=mock_client, generated_files={"existing_file.py": "content"}, namespace="test_namespace"
    )

    mock_state = Mock(spec=BaseState)

    with patch("vellum.workflows.utils.zip.extract_zip_files") as mock_extract:
        mock_extract.return_value = {"workflow.py": "mock content"}
        with patch("vellum.workflows.workflows.base.BaseWorkflow.load_from_module") as mock_load:
            mock_workflow_class = Mock()
            mock_load.side_effect = [Exception("Module not found"), mock_workflow_class]

            context.resolve_workflow_deployment("test-deployment", "latest", mock_state)

    mock_client.workflows.pull.assert_called_once()
    call_args = mock_client.workflows.pull.call_args
    expected_headers = {"X-Vellum-Always-Success": "true"}
    assert call_args[1]["request_options"]["additional_headers"] == expected_headers


def test_resolve_workflow_deployment__handles_api_error_gracefully():
    """
    Test that resolve_workflow_deployment returns None when API call fails (including 207 responses).
    """
    mock_client = Mock()
    error_body = {"success": False, "detail": "Version validation failed"}
    mock_client.workflows.pull.side_effect = ApiError(status_code=207, body=error_body)

    context = WorkflowContext(
        vellum_client=mock_client, generated_files={"existing_file.py": "content"}, namespace="test_namespace"
    )

    mock_state = Mock(spec=BaseState)

    result = context.resolve_workflow_deployment("test-deployment", "latest", mock_state)

    assert result is None


def test_resolve_workflow_deployment__handles_422_error_gracefully():
    """
    Test that resolve_workflow_deployment returns None when API call fails with 422 error.
    """
    mock_client = Mock()
    error_body = {"detail": "Version validation failed"}
    mock_client.workflows.pull.side_effect = ApiError(status_code=422, body=error_body)

    context = WorkflowContext(
        vellum_client=mock_client, generated_files={"existing_file.py": "content"}, namespace="test_namespace"
    )

    mock_state = Mock(spec=BaseState)

    result = context.resolve_workflow_deployment("test-deployment", "latest", mock_state)

    assert result is None


def test_resolve_workflow_deployment__api_call_includes_header():
    """
    Test that resolve_workflow_deployment includes X-Vellum-Always-Success header in API calls.
    """
    mock_client = Mock()
    mock_client.workflows.pull.return_value = iter([b"mock zip content"])

    context = WorkflowContext(
        vellum_client=mock_client, generated_files={"existing_file.py": "content"}, namespace="test_namespace"
    )

    mock_state = Mock(spec=BaseState)

    with patch("vellum.workflows.utils.zip.extract_zip_files") as mock_extract:
        mock_extract.return_value = {"workflow.py": "mock content"}
        with patch("vellum.workflows.workflows.base.BaseWorkflow.load_from_module") as mock_load:
            mock_load.side_effect = [Exception("Module not found"), Exception("Module still not found")]

            context.resolve_workflow_deployment("test-deployment", "latest", mock_state)

    mock_client.workflows.pull.assert_called_once()
    call_args = mock_client.workflows.pull.call_args
    expected_headers = {"X-Vellum-Always-Success": "true"}
    assert call_args[1]["request_options"]["additional_headers"] == expected_headers
