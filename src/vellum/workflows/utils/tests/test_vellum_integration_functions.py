from unittest.mock import MagicMock, patch

from vellum import FunctionDefinition
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.types.definition import VellumIntegrationToolDefinition
from vellum.workflows.utils.functions import compile_vellum_integration_tool_definition


class TestCompileVellumIntegrationToolDefinition:
    """Test cases for compile_vellum_integration_tool_definition function."""

    def test_successful_compilation(self):
        """Test successful compilation of VellumIntegrationToolDefinition."""
        # Setup
        tool_def = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="GITHUB",
            name="GITHUB_CREATE_AN_ISSUE",
            description="Create a GitHub issue",
        )

        # Mock VellumIntegrationService
        with patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_tool_definition.return_value = {
                "description": "Create a new issue in a GitHub repository",
                "input_parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Issue title"},
                        "body": {"type": "string", "description": "Issue body"},
                        "labels": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["title", "body"],
                },
            }
            mock_service_class.return_value = mock_service

            # Execute
            result = compile_vellum_integration_tool_definition(tool_def)

            # Verify
            assert isinstance(result, FunctionDefinition)
            assert result.name == "GITHUB_CREATE_AN_ISSUE"
            assert result.description == "Create a new issue in a GitHub repository"
            assert result.parameters == {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue body"},
                    "labels": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["title", "body"],
            }

            # Verify service was called correctly
            mock_service.get_tool_definition.assert_called_once_with(
                provider=VellumIntegrationProviderType.COMPOSIO, integration="GITHUB", action="GITHUB_CREATE_AN_ISSUE"
            )

    def test_fallback_on_service_error(self):
        """Test fallback to basic definition when service fails."""
        # Setup
        tool_def = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="SLACK",
            name="SLACK_SEND_MESSAGE",
            description="Send a Slack message",
        )

        # Mock VellumIntegrationService to raise an error
        with patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_tool_definition.side_effect = Exception("API error")
            mock_service_class.return_value = mock_service

            # Execute
            result = compile_vellum_integration_tool_definition(tool_def)

            # Verify fallback behavior
            assert isinstance(result, FunctionDefinition)
            assert result.name == "SLACK_SEND_MESSAGE"
            assert result.description == "Send a Slack message"
            assert result.parameters == {}

    def test_partial_tool_details(self):
        """Test compilation with partial tool details from service."""
        # Setup
        tool_def = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="JIRA",
            name="JIRA_CREATE_ISSUE",
            description="Create a JIRA issue",
        )

        # Mock VellumIntegrationService with partial response
        with patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
            mock_service = MagicMock()
            # Missing input_parameters in response
            mock_service.get_tool_definition.return_value = {"description": "Create a new issue in JIRA"}
            mock_service_class.return_value = mock_service

            # Execute
            result = compile_vellum_integration_tool_definition(tool_def)

            # Verify
            assert isinstance(result, FunctionDefinition)
            assert result.name == "JIRA_CREATE_ISSUE"
            assert result.description == "Create a new issue in JIRA"
            assert result.parameters == {}  # Should default to empty dict

    def test_missing_description_uses_default(self):
        """Test that missing description in service response uses tool definition's description."""
        # Setup
        tool_def = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="GMAIL",
            name="GMAIL_SEND_EMAIL",
            description="Send an email via Gmail",
        )

        # Mock VellumIntegrationService with no description
        with patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_tool_definition.return_value = {
                "input_parameters": {
                    "type": "object",
                    "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                }
            }
            mock_service_class.return_value = mock_service

            # Execute
            result = compile_vellum_integration_tool_definition(tool_def)

            # Verify
            assert result.description == "Send an email via Gmail"  # Uses tool_def.description
