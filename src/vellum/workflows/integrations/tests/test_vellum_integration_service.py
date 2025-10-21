import pytest
from unittest import mock
from uuid import uuid4

from vellum import ToolDefinitionIntegration
from vellum.client.types.components_schemas_composio_tool_definition import ComponentsSchemasComposioToolDefinition
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.exceptions import NodeException
from vellum.workflows.integrations.vellum_integration_service import VellumIntegrationService
from vellum.workflows.types.definition import VellumIntegrationToolDetails


def test_vellum_integration_service_get_tool_definition_success(vellum_client):
    """Test that tool definitions are successfully retrieved from Vellum API"""
    # GIVEN a mock client configured to return a tool definition
    mock_client = vellum_client
    tool_definition_response = ComponentsSchemasComposioToolDefinition(
        integration=ToolDefinitionIntegration(
            id=str(uuid4()),
            provider="COMPOSIO",
            name="GITHUB",
        ),
        label="GITHUB_CREATE_AN_ISSUE",
        name="GITHUB_CREATE_AN_ISSUE",
        description="Create a new issue in a GitHub repository",
        input_parameters={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository name"},
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue body"},
            },
            "required": ["repo", "title"],
        },
        output_parameters={},
    )
    mock_client.integrations.retrieve_integration_tool_definition.return_value = tool_definition_response

    # WHEN we request a tool definition
    service = VellumIntegrationService(client=mock_client)
    result = service.get_tool_definition(
        integration="GITHUB",
        provider="COMPOSIO",
        tool_name="GITHUB_CREATE_AN_ISSUE",
    )

    # THEN the tool definition should be returned with all expected fields
    assert isinstance(result, VellumIntegrationToolDetails)
    assert result.name == "GITHUB_CREATE_AN_ISSUE"
    assert result.description == "Create a new issue in a GitHub repository"
    assert result.provider == VellumIntegrationProviderType.COMPOSIO
    # Parameters should now be included in the tool details
    assert result.parameters is not None
    assert result.parameters["type"] == "object"
    assert "properties" in result.parameters
    assert "repo" in result.parameters["properties"]
    assert "title" in result.parameters["properties"]

    # AND the API should have been called with the correct parameters
    mock_client.integrations.retrieve_integration_tool_definition.assert_called_once_with(
        integration_name="GITHUB",
        integration_provider="COMPOSIO",
        tool_name="GITHUB_CREATE_AN_ISSUE",
    )


def test_vellum_integration_service_get_tool_definition_api_error(vellum_client):
    """Test that API errors are properly handled when retrieving tool definitions"""
    # GIVEN a mock client configured to raise an exception
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()
    mock_client.integrations.retrieve_integration_tool_definition.side_effect = Exception("Tool not found")

    # WHEN we attempt to get a tool definition for an invalid tool
    service = VellumIntegrationService(client=mock_client)

    # THEN it should raise a NodeException with appropriate error message
    with pytest.raises(NodeException) as exc_info:
        service.get_tool_definition(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="INVALID_TOOL",
        )

    assert "Failed to retrieve tool definition" in str(exc_info.value)
    assert "Tool not found" in str(exc_info.value)


def test_vellum_integration_service_execute_tool_success(vellum_client):
    """Test that tools are successfully executed via Vellum API"""
    # GIVEN a mock client configured to return a successful response
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()

    mock_response = mock.MagicMock()
    mock_response.data = {
        "success": True,
        "issue_id": 123,
        "issue_url": "https://github.com/user/repo/issues/123",
    }
    mock_client.integrations.execute_integration_tool.return_value = mock_response

    # WHEN we execute a tool with valid arguments
    service = VellumIntegrationService(client=mock_client)
    result = service.execute_tool(
        integration="GITHUB",
        provider="COMPOSIO",
        tool_name="GITHUB_CREATE_AN_ISSUE",
        arguments={
            "repo": "user/repo",
            "title": "Test Issue",
            "body": "Test body",
        },
    )

    # THEN the execution result should contain expected data
    assert result["success"] is True
    assert result["issue_id"] == 123
    assert result["issue_url"] == "https://github.com/user/repo/issues/123"

    # AND the API should have been called with correct parameters
    mock_client.integrations.execute_integration_tool.assert_called_once_with(
        integration_name="GITHUB",
        integration_provider="COMPOSIO",
        tool_name="GITHUB_CREATE_AN_ISSUE",
        arguments={
            "repo": "user/repo",
            "title": "Test Issue",
            "body": "Test body",
        },
    )


def test_vellum_integration_service_execute_tool_api_error(vellum_client):
    """Test that execution errors are properly handled"""
    # GIVEN a mock client configured to raise an exception
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()
    mock_client.integrations.execute_integration_tool.side_effect = Exception("Authentication failed")

    # WHEN we attempt to execute a tool that encounters an error
    service = VellumIntegrationService(client=mock_client)

    # THEN it should raise a NodeException with appropriate error message
    with pytest.raises(NodeException) as exc_info:
        service.execute_tool(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={"repo": "user/repo"},
        )

    assert "Failed to execute tool" in str(exc_info.value)
    assert "Authentication failed" in str(exc_info.value)


def test_vellum_integration_service_execute_tool_empty_response(vellum_client):
    """Test that empty response data is handled gracefully"""
    # GIVEN a mock client configured to return an empty response
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()

    mock_response = mock.MagicMock()
    mock_response.data = {}
    mock_client.integrations.execute_integration_tool.return_value = mock_response

    # WHEN we execute a tool that returns empty data
    service = VellumIntegrationService(client=mock_client)
    result = service.execute_tool(
        integration="SLACK",
        provider="COMPOSIO",
        tool_name="SLACK_SEND_MESSAGE",
        arguments={
            "channel": "#general",
            "message": "Hello, world!",
        },
    )

    # THEN an empty dictionary should be returned without errors
    assert result == {}


def test_vellum_integration_service_multiple_tool_executions(vellum_client):
    """Test that the service handles multiple sequential tool executions"""
    # GIVEN a mock client configured to return different responses for multiple calls
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()

    responses = [
        mock.MagicMock(data={"result": "first"}),
        mock.MagicMock(data={"result": "second"}),
    ]
    mock_client.integrations.execute_integration_tool.side_effect = responses

    # WHEN we execute multiple tools in sequence
    service = VellumIntegrationService(client=mock_client)

    result1 = service.execute_tool(
        integration="GITHUB",
        provider="COMPOSIO",
        tool_name="TOOL_1",
        arguments={"arg": "val1"},
    )

    result2 = service.execute_tool(
        integration="SLACK",
        provider="COMPOSIO",
        tool_name="TOOL_2",
        arguments={"arg": "val2"},
    )

    # THEN each tool execution should return its respective result
    assert result1["result"] == "first"
    assert result2["result"] == "second"

    # AND the API should have been called twice
    assert mock_client.integrations.execute_integration_tool.call_count == 2


def test_vellum_integration_service_execute_tool_structured_403_with_integration(vellum_client):
    """Test structured 403 responses with integration field (current backend format)"""
    from vellum.client.core.api_error import ApiError
    from vellum.workflows.errors.types import WorkflowErrorCode

    # GIVEN a mock client configured to raise a structured 403 error with integration
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()

    # Mock current backend structure with integration as direct field
    structured_error_body = {
        "code": "INTEGRATION_CREDENTIALS_UNAVAILABLE",
        "message": "You must authenticate with this integration before you can execute this tool.",
        "integration": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "provider": "COMPOSIO",
            "name": "GITHUB",
        },
    }
    mock_client.integrations.execute_integration_tool.side_effect = ApiError(
        status_code=403,
        body=structured_error_body,
    )

    # WHEN we attempt to execute a tool without credentials
    service = VellumIntegrationService(client=mock_client)
    with pytest.raises(NodeException) as exc_info:
        service.execute_tool(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={"repo": "user/repo"},
        )

    # THEN it should raise NodeException with INTEGRATION_CREDENTIALS_UNAVAILABLE code
    assert exc_info.value.code == WorkflowErrorCode.INTEGRATION_CREDENTIALS_UNAVAILABLE

    # AND the error message should match the backend response
    assert "You must authenticate with this integration" in exc_info.value.message

    # AND raw_data should contain integration details nested under "integration" key
    assert exc_info.value.raw_data is not None
    assert exc_info.value.raw_data["integration"]["id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert exc_info.value.raw_data["integration"]["name"] == "GITHUB"
    assert exc_info.value.raw_data["integration"]["provider"] == "COMPOSIO"


def test_vellum_integration_service_execute_tool_legacy_403_error(vellum_client):
    """Test backward compatibility with legacy 403 responses (before PR #14857)"""
    from vellum.client.core.api_error import ApiError
    from vellum.workflows.errors.types import WorkflowErrorCode

    # GIVEN a mock client configured to raise a legacy 403 error
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()

    legacy_error_body = {"detail": "You do not have permission to execute this tool."}
    mock_client.integrations.execute_integration_tool.side_effect = ApiError(
        status_code=403,
        body=legacy_error_body,
    )

    # WHEN we attempt to execute a tool that returns a legacy 403 error
    service = VellumIntegrationService(client=mock_client)
    with pytest.raises(NodeException) as exc_info:
        service.execute_tool(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={"repo": "user/repo"},
        )

    # THEN it should use the generic PROVIDER_CREDENTIALS_UNAVAILABLE code
    assert exc_info.value.code == WorkflowErrorCode.PROVIDER_CREDENTIALS_UNAVAILABLE

    # AND the message should match the legacy format
    assert "You do not have permission" in exc_info.value.message

    # AND raw_data should be None (no integration details available)
    assert exc_info.value.raw_data is None
