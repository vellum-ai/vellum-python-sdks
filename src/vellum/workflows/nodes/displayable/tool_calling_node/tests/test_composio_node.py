import pytest
from contextlib import contextmanager
import json
from unittest.mock import Mock, patch

from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.nodes.displayable.tool_calling_node.utils import ComposioNode
from vellum.workflows.types.definition import ComposioToolDefinition


@pytest.fixture
def composio_tool():
    """Fixture for a sample ComposioToolDefinition."""
    return ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )


@pytest.fixture
def mock_state():
    """Fixture for a mock ToolCallingState."""
    state = Mock(spec=ToolCallingState)
    state.chat_history = Mock()
    return state


@pytest.fixture
def composio_node(composio_tool, mock_state):
    """Fixture for a configured ComposioNode instance."""
    node = ComposioNode()
    node.composio_tool = composio_tool
    node.function_call_output = []
    node.state = mock_state

    return node


@contextmanager
def mock_composio_service(monkeypatch, api_key="test-api-key", service_return_value=None):
    """Context manager to mock the Composio environment and service."""
    if service_return_value is None:
        service_return_value = {"result": "success"}

    # Set or delete the environment variable
    if api_key is not None:
        monkeypatch.setenv("COMPOSIO_API_KEY", api_key)
    else:
        monkeypatch.delenv("COMPOSIO_API_KEY", raising=False)

    with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
        mock_service.return_value.execute_tool.return_value = service_return_value
        yield mock_service


def test_composio_node_extracts_and_executes_with_arguments(composio_node, monkeypatch):
    """Test that ComposioNode correctly extracts arguments and executes the tool."""
    # GIVEN a function call with arguments
    function_call = FunctionCall(
        arguments={"title": "Test Issue", "body": "This is a test issue"},
        id="call_123",
        name="github_create_issue",
    )
    composio_node.function_call_output = [FunctionCallVellumValue(value=function_call)]

    # WHEN we run the node
    with mock_composio_service(monkeypatch) as mock_service:
        list(composio_node.run())

    # THEN the tool should be executed with correct arguments
    mock_service.return_value.execute_tool.assert_called_once_with(
        tool_name="GITHUB_CREATE_AN_ISSUE", arguments={"title": "Test Issue", "body": "This is a test issue"}
    )


def test_composio_node_no_api_key_raises_exception(composio_node, monkeypatch):
    """Test that ComposioNode raises exception when no API key is found."""
    # WHEN we run the node with no API key
    with mock_composio_service(monkeypatch, api_key=None):
        # THEN it should raise a NodeException
        with pytest.raises(NodeException) as exc_info:
            list(composio_node.run())

    assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
    assert "No Composio API key found in environment variables" in str(exc_info.value)


def test_composio_node_handles_service_errors(composio_node, monkeypatch):
    """Test that ComposioNode handles ComposioService execution errors."""
    # GIVEN an API key is set
    monkeypatch.setenv("COMPOSIO_API_KEY", "test-api-key")

    # WHEN the service raises an exception
    with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
        mock_service.return_value.execute_tool.side_effect = Exception("API connection failed")

        # THEN it should raise a NodeException with proper error details
        with pytest.raises(NodeException) as exc_info:
            list(composio_node.run())

    assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
    assert "Error executing Composio tool 'GITHUB_CREATE_AN_ISSUE': API connection failed" in str(exc_info.value)


def test_composio_node_updates_chat_history(composio_node, monkeypatch):
    """Test that ComposioNode correctly updates the chat history with tool results."""
    # GIVEN an expected tool execution result
    expected_result = {"issue_url": "https://github.com/test/repo/issues/1", "issue_number": 42}

    # WHEN we run the node
    with mock_composio_service(monkeypatch, service_return_value=expected_result):
        list(composio_node.run())

    # THEN chat history should be updated with the tool result
    assert len(composio_node.state.chat_history.append.call_args_list) == 1
    chat_message = composio_node.state.chat_history.append.call_args[0][0]

    assert chat_message.role == "FUNCTION"
    assert chat_message.content.type == "STRING"
    assert chat_message.content.value == json.dumps(expected_result)
