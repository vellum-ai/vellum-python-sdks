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
from vellum.workflows.nodes.displayable.tool_calling_node.utils import ComposioNode
from vellum.workflows.types.definition import ComposioToolDefinition


@pytest.fixture
def composio_tool():
    """Fixture for a sample ComposioToolDefinition."""
    return ComposioToolDefinition(
        toolkit="GITHUB", action="GITHUB_CREATE_AN_ISSUE", description="Create a new issue in a GitHub repository"
    )


@pytest.fixture
def composio_function_node(composio_tool):
    """Fixture for a ComposioNode instance."""
    # Create a dynamic class similar to how create_function_node does it
    node_class = type(
        "TestComposioNode",
        (ComposioNode,),
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
    """Test that ComposioNode is initialized correctly."""
    # GIVEN a ComposioNode instance and a composio tool definition

    # WHEN we check the node attributes

    # THEN the node should be properly initialized
    assert composio_function_node.composio_tool == composio_tool
    assert composio_function_node.function_call_output == []


def test_composio_function_node_extracts_arguments_from_function_call(composio_function_node, mock_state):
    """Test that ComposioNode correctly extracts arguments from function call."""
    # GIVEN a ComposioNode with function call output containing arguments
    function_call = FunctionCall(
        arguments={"title": "Test Issue", "body": "This is a test issue"},
        id="call_123",
        name="github_create_issue",
        state="FULFILLED",
    )
    function_call_output: List[PromptOutput] = [FunctionCallVellumValue(value=function_call)]
    composio_function_node.function_call_output = function_call_output
    composio_function_node.state = mock_state

    # WHEN we run the node with mocked Composio service
    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"issue_url": "https://github.com/test/repo/issues/1"}
            list(composio_function_node.run())

    # THEN ComposioService.execute_tool should be called with correct arguments
    mock_service.return_value.execute_tool.assert_called_once_with(
        tool_name="GITHUB_CREATE_AN_ISSUE", arguments={"title": "Test Issue", "body": "This is a test issue"}
    )


@pytest.mark.parametrize(
    "function_call_output,scenario_name",
    [
        ([], "no_function_call_output"),
        (
            [FunctionCallVellumValue(value=FunctionCall(arguments={}, id="call_123", name="test", state="FULFILLED"))],
            "empty_arguments",
        ),
        ([StringVellumValue(value="This is a string response")], "non_function_call_output"),
    ],
)
def test_composio_function_node_handles_missing_arguments(
    composio_function_node, mock_state, function_call_output, scenario_name
):
    """Test that ComposioNode handles various cases where function call arguments are missing or empty."""
    # GIVEN a ComposioNode with different function call output scenarios
    composio_function_node.function_call_output = function_call_output
    composio_function_node.state = mock_state

    # WHEN we run the node with mocked Composio service
    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"result": "success"}
            list(composio_function_node.run())

    # THEN ComposioService.execute_tool should be called with empty arguments
    mock_service.return_value.execute_tool.assert_called_once_with(tool_name="GITHUB_CREATE_AN_ISSUE", arguments={})


@pytest.mark.parametrize(
    "env_vars",
    [
        {"COMPOSIO_API_KEY": "test_key_1"},
        {"MY_COMPOSIO_KEY": "test_key_2"},
        {"composio_secret": "test_key_3"},  # lowercase
    ],
)
def test_composio_function_node_api_key_discovery(composio_function_node, mock_state, env_vars):
    """Test that ComposioNode finds Composio API key from environment variables."""
    # GIVEN a ComposioNode and environment variables containing composio keys
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    # WHEN we run the node with different environment variable configurations
    with patch.dict(os.environ, env_vars, clear=True):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = {"result": "success"}
            list(composio_function_node.run())

    # THEN ComposioService should be initialized with the correct API key
    expected_key = list(env_vars.values())[0]
    mock_service.assert_called_once_with(api_key=expected_key)


def test_composio_function_node_no_api_key_raises_exception(composio_function_node, mock_state):
    """Test that ComposioNode raises exception when no Composio API key is found."""
    # GIVEN a ComposioNode and no Composio API key in environment variables
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    # WHEN we run the node with cleared environment variables
    with patch.dict(os.environ, {}, clear=True):
        # THEN it should raise a NodeException
        with pytest.raises(NodeException) as exc_info:
            list(composio_function_node.run())

        assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
        assert "No Composio API key found in environment variables" in str(exc_info.value)


def test_composio_function_node_composio_service_error(composio_function_node, mock_state):
    """Test that ComposioNode handles ComposioService execution errors."""
    # GIVEN a ComposioNode and a mocked ComposioService that will fail
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state

    # WHEN we run the node and the service raises an exception
    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.side_effect = Exception("API connection failed")

            # THEN it should raise a NodeException with proper error details
            with pytest.raises(NodeException) as exc_info:
                list(composio_function_node.run())

            assert exc_info.value.code == WorkflowErrorCode.NODE_EXECUTION
            assert "Error executing Composio tool 'GITHUB_CREATE_AN_ISSUE': API connection failed" in str(
                exc_info.value
            )


def test_composio_function_node_updates_chat_history(composio_function_node, mock_state):
    """Test that ComposioNode correctly updates the chat history with tool results."""
    # GIVEN a ComposioNode and expected tool execution result
    composio_function_node.function_call_output = []
    composio_function_node.state = mock_state
    expected_result = {"issue_url": "https://github.com/test/repo/issues/1", "issue_number": 42}

    # WHEN we run the node with mocked successful Composio service execution
    with patch.dict(os.environ, {"COMPOSIO_API_KEY": "test_key"}):
        with patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service:
            mock_service.return_value.execute_tool.return_value = expected_result
            list(composio_function_node.run())

    # THEN chat history should be updated with the tool result
    assert len(mock_state.chat_history.append.call_args_list) == 1
    chat_message = mock_state.chat_history.append.call_args[0][0]

    assert chat_message.role == "FUNCTION"
    assert chat_message.content.type == "STRING"

    # Check that the content is the JSON-serialized result
    expected_json = json.dumps(expected_result)
    assert chat_message.content.value == expected_json
