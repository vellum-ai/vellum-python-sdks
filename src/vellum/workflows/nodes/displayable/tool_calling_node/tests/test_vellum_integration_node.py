import pytest
import json
from unittest.mock import MagicMock, patch

from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.nodes.displayable.tool_calling_node.utils import VellumIntegrationNode
from vellum.workflows.types.definition import VellumIntegrationToolDefinition


class TestVellumIntegrationNode:
    """Test cases for VellumIntegrationNode."""

    def test_successful_tool_execution(self):
        """Test successful execution of a Vellum Integration tool."""
        # Setup
        tool_definition = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="GITHUB",
            name="GITHUB_CREATE_AN_ISSUE",
            description="Create a GitHub issue",
        )

        # Mock the function call output
        function_call = FunctionCallVellumValue(
            type="FUNCTION_CALL",
            value=None,
            id="test_call_id",
            name="GITHUB_CREATE_AN_ISSUE",
            arguments={"title": "Test Issue", "body": "Test body"},
        )

        # Create node instance
        node = VellumIntegrationNode()
        node.vellum_integration_tool = tool_definition
        node.function_call_output = [function_call]

        # Initialize state
        state = ToolCallingState()
        state.current_prompt_output_index = 0
        state.chat_history = []
        node.state = state

        # Mock VellumIntegrationService
        with patch(
            "vellum.workflows.integrations.vellum_integration_service.VellumIntegrationService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.execute_integration_tool.return_value = {
                "issue_id": 123,
                "url": "https://github.com/test/test/issues/123",
            }
            mock_service_class.return_value = mock_service

            # Execute
            list(node.run())

            # Verify service was called correctly
            mock_service.execute_integration_tool.assert_called_once_with(
                provider=VellumIntegrationProviderType.COMPOSIO,
                integration="GITHUB",
                name="GITHUB_CREATE_AN_ISSUE",
                arguments={"title": "Test Issue", "body": "Test body"},
            )

            # Verify chat history was updated
            assert len(state.chat_history) == 1
            assert state.chat_history[0].role == "FUNCTION"
            assert json.loads(state.chat_history[0].content.value) == {
                "issue_id": 123,
                "url": "https://github.com/test/test/issues/123",
            }
            assert state.chat_history[0].source == "test_call_id"

            # Verify state was updated
            assert state.current_function_calls_processed == 1
            assert state.current_prompt_output_index == 1

    def test_tool_execution_with_error(self):
        """Test handling of errors during tool execution."""
        # Setup
        tool_definition = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="SLACK",
            name="SLACK_SEND_MESSAGE",
            description="Send a Slack message",
        )

        # Mock the function call output
        function_call = FunctionCallVellumValue(
            type="FUNCTION_CALL",
            value=None,
            id="test_call_id",
            name="SLACK_SEND_MESSAGE",
            arguments={"channel": "general", "message": "Test message"},
        )

        # Create node instance
        node = VellumIntegrationNode()
        node.vellum_integration_tool = tool_definition
        node.function_call_output = [function_call]

        # Initialize state
        state = ToolCallingState()
        state.current_prompt_output_index = 0
        state.chat_history = []
        node.state = state

        # Mock VellumIntegrationService to raise an error
        with patch(
            "vellum.workflows.integrations.vellum_integration_service.VellumIntegrationService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.execute_integration_tool.side_effect = Exception("API rate limit exceeded")
            mock_service_class.return_value = mock_service

            # Execute and expect NodeException
            with pytest.raises(NodeException) as exc_info:
                list(node.run())

            assert "Error executing Vellum Integration tool 'SLACK_SEND_MESSAGE'" in str(exc_info.value.message)
            assert "API rate limit exceeded" in str(exc_info.value.message)

    def test_extract_function_arguments_with_no_arguments(self):
        """Test extracting function arguments when none are provided."""
        # Setup
        tool_definition = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="GITHUB",
            name="GITHUB_LIST_REPOS",
            description="List GitHub repositories",
        )

        # Mock the function call output with no arguments
        function_call = FunctionCallVellumValue(
            type="FUNCTION_CALL", value=None, id="test_call_id", name="GITHUB_LIST_REPOS", arguments=None
        )

        # Create node instance
        node = VellumIntegrationNode()
        node.vellum_integration_tool = tool_definition
        node.function_call_output = [function_call]

        # Initialize state
        state = ToolCallingState()
        state.current_prompt_output_index = 0
        state.chat_history = []
        node.state = state

        # Mock VellumIntegrationService
        with patch(
            "vellum.workflows.integrations.vellum_integration_service.VellumIntegrationService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.execute_integration_tool.return_value = {"repos": []}
            mock_service_class.return_value = mock_service

            # Execute
            list(node.run())

            # Verify service was called with empty arguments
            mock_service.execute_integration_tool.assert_called_once_with(
                provider=VellumIntegrationProviderType.COMPOSIO,
                integration="GITHUB",
                name="GITHUB_LIST_REPOS",
                arguments={},
            )

    def test_vellum_integration_node_with_multiple_outputs(self):
        """Test VellumIntegrationNode with multiple function call outputs."""
        # Setup
        tool_definition = VellumIntegrationToolDefinition(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration="JIRA",
            name="JIRA_CREATE_ISSUE",
            description="Create a JIRA issue",
        )

        # Create multiple function call outputs
        function_call_1 = FunctionCallVellumValue(
            type="FUNCTION_CALL", value=None, id="call_1", name="OTHER_FUNCTION", arguments={}
        )
        function_call_2 = FunctionCallVellumValue(
            type="FUNCTION_CALL",
            value=None,
            id="call_2",
            name="JIRA_CREATE_ISSUE",
            arguments={"project": "TEST", "summary": "Test issue"},
        )

        prompt_outputs = [function_call_1, function_call_2]

        # Create node instance
        node = VellumIntegrationNode()
        node.vellum_integration_tool = tool_definition
        node.function_call_output = prompt_outputs

        # Initialize state pointing to second output
        state = ToolCallingState()
        state.current_prompt_output_index = 1
        state.chat_history = []
        node.state = state

        # Mock VellumIntegrationService
        with patch(
            "vellum.workflows.integrations.vellum_integration_service.VellumIntegrationService"
        ) as mock_service_class:
            mock_service = MagicMock()
            mock_service.execute_integration_tool.return_value = {"issue_key": "TEST-123"}
            mock_service_class.return_value = mock_service

            # Execute
            list(node.run())

            # Verify correct function call was used
            mock_service.execute_integration_tool.assert_called_once_with(
                provider=VellumIntegrationProviderType.COMPOSIO,
                integration="JIRA",
                name="JIRA_CREATE_ISSUE",
                arguments={"project": "TEST", "summary": "Test issue"},
            )

            # Verify correct function call ID was used
            assert state.chat_history[0].source == "call_2"
