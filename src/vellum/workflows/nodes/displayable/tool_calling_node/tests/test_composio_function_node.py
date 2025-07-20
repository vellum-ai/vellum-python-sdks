import pytest
import json
import os
from unittest.mock import Mock, patch
from typing import List

from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.tool_calling_node.state import ToolCallingState
from vellum.workflows.nodes.displayable.tool_calling_node.utils import ComposioFunctionNode
from vellum.workflows.types.definition import ComposioToolDefinition


@pytest.fixture
def composio_tool():
    """Fixture for a sample ComposioToolDefinition."""
    return ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )


@pytest.fixture
def composio_function_node(composio_tool):
    """Fixture for a ComposioFunctionNode instance."""
    # Create a dynamic class similar to how create_function_node does it
    node_class = type(
        "TestComposioFunctionNode",
        (ComposioFunctionNode,),
        {
            "composio_tool": composio_tool,
            "function_call_output": [],
            "__module__": __name__,
        },
    )
    return node_class()


@pytest.fixture
def mock_state():
    """Fixture for a mock ToolCallingState."""
    state = Mock(spec=ToolCallingState)
    state.chat_history = Mock()
    return state


def test_composio_function_node_initialization(composio_function_node, composio_tool):
    """Test that ComposioFunctionNode is initialized correctly."""
    assert composio_function_node.composio_tool == composio_tool
    assert composio_function_node.function_call_output == []


def test_composio_function_node_extracts_arguments_from_function_call(composio_function_node, mock_state):
    """Test that ComposioFunctionNode correctly extracts arguments from function call."""
    # Setup function call output with arguments
    function_call = FunctionCall(
        arguments={"title": "Test Issue", "body": "This is a test issue"},
        id="call_123",
        name="github_create_issue",
        state="FULFILLED",
    )
    function_call_output: List[PromptOutput] = [FunctionCallVellumValue(value=function_call)]
    composio_function_node.function_call_output = function_call_output
    composio_function_node.state = mock_state

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"issue_url": "https://github.com/test/repo/issues/1"}

            # Run the node
            list(composio_function_node.run())

            # Check that ComposioService.execute_tool was called with correct arguments
            mock_service.return_value.execute_tool.assert_called_once_with(
                tool_name="GITHUB_CREATE_AN_ISSUE", arguments={"title": "Test Issue", "body": "This is a test issue"}
            )


def test_composio_function_node_handles_empty_arguments(composio_function_node, mock_state):
    """Test that ComposioFunctionNode handles empty function call arguments."""
    # Setup function call output with no arguments
    function_call = FunctionCall(arguments={}, id="call_123", name="github_create_issue", state="FULFILLED")
    function_call_output: List[PromptOutput] = [FunctionCallVellumValue(value=function_call)]
    composio_function_node.function_call_output = function_call_output
    composio_function_node.state = mock_state

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"result": "success"}

            # Run the node
            list(composio_function_node.run())

            # Check that ComposioService.execute_tool was called with empty arguments
            mock_service.return_value.execute_tool.assert_called_once_with(
                tool_name="GITHUB_CREATE_AN_ISSUE", arguments={}
            )


def test_composio_function_node_handles_no_function_call_output(composio_function_node, mock_state):
    """Test that ComposioFunctionNode handles case where there's no function call output."""
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"result": "success"}

            # Run the node
            list(composio_function_node.run())

            # Check that ComposioService.execute_tool was called with empty arguments
            mock_service.return_value.execute_tool.assert_called_once_with(
                tool_name="GITHUB_CREATE_AN_ISSUE", arguments={}
            )


def test_composio_function_node_handles_non_function_call_output(composio_function_node, mock_state):
    """Test that ComposioFunctionNode handles non-function call output types."""
    # Setup with STRING output instead of FUNCTION_CALL
    string_output: List[PromptOutput] = [StringVellumValue(value="This is a string response")]
    composio_function_node.function_call_output = string_output
    composio_function_node.state = mock_state

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"result": "success"}

            # Run the node
            list(composio_function_node.run())

            # Check that ComposioService.execute_tool was called with empty arguments
            mock_service.return_value.execute_tool.assert_called_once_with(
                tool_name="GITHUB_CREATE_AN_ISSUE", arguments={}
            )


def test_composio_function_node_api_key_discovery(composio_function_node, mock_state):
    """Test that ComposioFunctionNode finds Composio API key from environment variables."""
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    # Test various environment variable names containing "composio"
    test_cases = [
        {"COMPOSIO_API_KEY": "test_key_1"},
        {"MY_COMPOSIO_KEY": "test_key_2"},
        {"COMPOSIO_TOKEN": "test_key_3"},
        {"composio_secret": "test_key_4"},  # lowercase
    ]

    for env_vars in test_cases:
        with patch.dict(os.environ, env_vars, clear=True):
            with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
                mock_service.return_value.execute_tool.return_value = {"result": "success"}

                # Run the node
                list(composio_function_node.run())

                # Check that ComposioService was initialized with the correct API key
                expected_key = list(env_vars.values())[0]
                mock_service.assert_called_once_with(api_key=expected_key)


def test_composio_function_node_no_api_key_raises_exception(composio_function_node, mock_state):
    """Test that ComposioFunctionNode raises exception when no Composio API key is found."""
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    # Clear all environment variables
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(NodeException) as exc_info:
            list(composio_function_node.run())

        assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
        assert "No Composio API key found in environment variables" in str(exc_info.value)


def test_composio_function_node_composio_service_error(composio_function_node, mock_state):
    """Test that ComposioFunctionNode handles ComposioService execution errors."""
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            # Make the service raise an exception
            mock_service.return_value.execute_tool.side_effect = Exception("API connection failed")

            with pytest.raises(NodeException) as exc_info:
                list(composio_function_node.run())

            assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
            assert "Error executing Composio tool 'GITHUB_CREATE_AN_ISSUE': API connection failed" in str(
                exc_info.value
            )


def test_composio_function_node_updates_chat_history(composio_function_node, mock_state):
    """Test that ComposioFunctionNode correctly updates the chat history with tool results."""
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    expected_result = {"issue_url": "https://github.com/test/repo/issues/1", "issue_number": 42}

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = expected_result

            # Run the node
            list(composio_function_node.run())

            # Check that chat history was updated
            assert len(mock_state.chat_history.append.call_args_list) == 1
            chat_message = mock_state.chat_history.append.call_args[0][0]

            assert chat_message.role == "FUNCTION"
            assert chat_message.content.type == "STRING"

            # Check that the content is the JSON-serialized result
            expected_json = json.dumps(expected_result)
            assert chat_message.content.value == expected_json


def test_composio_function_node_run_returns_empty_iterator(composio_function_node, mock_state):
    """Test that ComposioFunctionNode.run() returns an empty iterator."""
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"result": "success"}

            # Run the node and collect outputs
            outputs = list(composio_function_node.run())

            # Should return empty list (no BaseOutput objects)
            assert outputs == []
