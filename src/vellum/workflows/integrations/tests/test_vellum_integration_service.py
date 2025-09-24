import pytest
from unittest import mock

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.exceptions import NodeException
from vellum.workflows.integrations.vellum_integration_service import VellumIntegrationService
from vellum.workflows.types.definition import VellumIntegrationToolDetails


def test_vellum_integration_service_get_tool_definition_success(vellum_client):
    """Test that tool definitions are successfully retrieved from Vellum API"""
    mock_client = vellum_client
    mock_client.integrations = mock.MagicMock()

    mock_response = mock.MagicMock()
    mock_response.name = "GITHUB_CREATE_AN_ISSUE"
    mock_response.description = "Create a new issue in a GitHub repository"
    mock_response.parameters = {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "Repository name"},
            "title": {"type": "string", "description": "Issue title"},
            "body": {"type": "string", "description": "Issue body"},
        },
        "required": ["repo", "title"],
    }
    mock_response.provider = "COMPOSIO"

    mock_client.integrations.retrieve_integration_tool_definition.return_value = mock_response

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
        integration="GITHUB",
        provider="COMPOSIO",
        tool_name="GITHUB_CREATE_AN_ISSUE",
    )


def test_vellum_integration_service_get_tool_definition_api_error(vellum_client):
    """Test that API errors are properly handled when retrieving tool definitions"""
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
        integration="GITHUB",
        provider="COMPOSIO",
        tool_name="GITHUB_CREATE_AN_ISSUE",
        arguments={
            "repo": "user/repo",
            "title": "Test Issue",
            "body": "Test body",
        },
    )


def test_vellum_integration_service_execute_tool_api_error(vellum_client):
    """Test that execution errors are properly handled"""
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
