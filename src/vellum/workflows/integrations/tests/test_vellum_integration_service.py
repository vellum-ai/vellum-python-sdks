import pytest
from unittest.mock import MagicMock, patch

from vellum.workflows.exceptions import NodeException
from vellum.workflows.integrations.vellum_integration_service import VellumIntegrationService


class TestVellumIntegrationService:
    """Test suite for VellumIntegrationService."""

    @patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
    def test_get_tool_definition_success(self, mock_create_client):
        """Test successful retrieval of tool definition."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        mock_response = MagicMock()
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

        service = VellumIntegrationService()

        # Execute
        result = service.get_tool_definition(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
        )

        # Assert
        assert result["name"] == "GITHUB_CREATE_AN_ISSUE"
        assert result["description"] == "Create a new issue in a GitHub repository"
        assert result["provider"] == "COMPOSIO"
        assert "properties" in result["parameters"]
        assert "repo" in result["parameters"]["properties"]

        mock_client.integrations.retrieve_integration_tool_definition.assert_called_once_with(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="GITHUB_CREATE_AN_ISSUE",
        )

    @patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
    def test_get_tool_definition_failure(self, mock_create_client):
        """Test handling of errors when retrieving tool definition."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        mock_client.integrations.retrieve_integration_tool_definition.side_effect = Exception("Tool not found")

        service = VellumIntegrationService()

        # Execute & Assert
        with pytest.raises(NodeException) as exc_info:
            service.get_tool_definition(
                integration="GITHUB",
                provider="COMPOSIO",
                tool_name="INVALID_TOOL",
            )

        assert "Failed to retrieve tool definition" in str(exc_info.value)
        assert "Tool not found" in str(exc_info.value)

    @patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
    def test_execute_tool_success(self, mock_create_client):
        """Test successful tool execution."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = {
            "success": True,
            "issue_id": 123,
            "issue_url": "https://github.com/user/repo/issues/123",
        }

        mock_client.integrations.execute_integration_tool.return_value = mock_response

        service = VellumIntegrationService()

        # Execute
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

        # Assert
        assert result["success"] is True
        assert result["issue_id"] == 123
        assert result["issue_url"] == "https://github.com/user/repo/issues/123"

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

    @patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
    def test_execute_tool_failure(self, mock_create_client):
        """Test handling of errors during tool execution."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        mock_client.integrations.execute_integration_tool.side_effect = Exception("Authentication failed")

        service = VellumIntegrationService()

        # Execute & Assert
        with pytest.raises(NodeException) as exc_info:
            service.execute_tool(
                integration="GITHUB",
                provider="COMPOSIO",
                tool_name="GITHUB_CREATE_AN_ISSUE",
                arguments={"repo": "user/repo"},
            )

        assert "Failed to execute tool" in str(exc_info.value)
        assert "Authentication failed" in str(exc_info.value)

    @patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
    def test_execute_tool_empty_response_data(self, mock_create_client):
        """Test handling of empty response data from tool execution."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        mock_response = MagicMock()
        mock_response.data = {}

        mock_client.integrations.execute_integration_tool.return_value = mock_response

        service = VellumIntegrationService()

        # Execute
        result = service.execute_tool(
            integration="SLACK",
            provider="COMPOSIO",
            tool_name="SLACK_SEND_MESSAGE",
            arguments={
                "channel": "#general",
                "message": "Hello, world!",
            },
        )

        # Assert
        assert result == {}

    @patch("vellum.workflows.integrations.vellum_integration_service.create_vellum_client")
    def test_multiple_tool_executions(self, mock_create_client):
        """Test that the service can handle multiple tool executions."""
        # Setup
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client

        service = VellumIntegrationService()

        # Mock different responses for different tools
        responses = [
            MagicMock(data={"result": "first"}),
            MagicMock(data={"result": "second"}),
        ]
        mock_client.integrations.execute_integration_tool.side_effect = responses

        # Execute
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

        # Assert
        assert result1["result"] == "first"
        assert result2["result"] == "second"
        assert mock_client.integrations.execute_integration_tool.call_count == 2
