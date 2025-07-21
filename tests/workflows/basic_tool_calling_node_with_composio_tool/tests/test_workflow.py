from unittest import mock
from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.basic_tool_calling_node_with_composio_tool.workflow import (
    BasicToolCallingNodeWithComposioToolWorkflow,
    Inputs,
    github_create_issue_tool,
)


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, vellum_client, mock_uuid4_generator, monkeypatch):
    """
    Test that the ComposioToolCallingNode workflow returns the expected outputs
    when successfully executing a Composio tool.
    """

    # Mock ComposioService
    mock_composio_result = {
        "issue": {
            "id": 123,
            "title": "Test Issue",
            "body": "This is a test issue created via Composio",
            "url": "https://github.com/owner/repo/issues/123",
        }
    }

    with mock.patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service_class:
        mock_service_instance = mock.Mock()
        mock_service_instance.execute_tool.return_value = mock_composio_result
        mock_service_class.return_value = mock_service_instance

        # Set API key via monkeypatch
        monkeypatch.setenv("COMPOSIO_API_KEY", "test_api_key_123")

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())

            call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
            expected_outputs: List[PromptOutput]
            if call_count == 1:
                expected_outputs = [
                    FunctionCallVellumValue(
                        value=FunctionCall(
                            arguments={
                                "owner": "test-owner",
                                "repo": "test-repo",
                                "title": "Bug in authentication",
                                "body": "There seems to be an issue with login functionality",
                            },
                            id="call_composio_github_create_issue",
                            name="github_create_an_issue",
                            state="FULFILLED",
                        ),
                    ),
                ]
            else:
                expected_outputs = [
                    StringVellumValue(
                        value=(
                            "I've successfully created the GitHub issue. "
                            "You can view it at: https://github.com/owner/repo/issues/123"
                        )
                    )
                ]

            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        # Set up the mock to return our events
        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        # GIVEN a Composio tool calling workflow
        workflow = BasicToolCallingNodeWithComposioToolWorkflow()

        # WHEN the workflow is executed
        terminal_event = workflow.run(
            Inputs(query=("Create an issue in the test-owner/test-repo repository about authentication bug"))
        )

        # Then assert
        assert terminal_event.name == "workflow.execution.fulfilled"
        assert terminal_event.outputs.text == (
            "I've successfully created the GitHub issue. You can view it at: https://github.com/owner/repo/issues/123"
        )

        # AND the chat history contains the function call and result
        assert len(terminal_event.outputs.chat_history) == 3

        # Function call message
        function_call_msg = terminal_event.outputs.chat_history[0]
        assert function_call_msg.role == "ASSISTANT"
        assert function_call_msg.content.type == "FUNCTION_CALL"
        assert function_call_msg.content.value.name == "github_create_an_issue"

        # Function result message
        function_result_msg = terminal_event.outputs.chat_history[1]
        assert function_result_msg.role == "FUNCTION"
        assert function_result_msg.content.type == "STRING"
        # The result should be the JSON serialized version of mock_composio_result
        assert mock_composio_result["issue"]["id"] == 123  # Verify the mock result is in the response

        # Final assistant message
        final_msg = terminal_event.outputs.chat_history[2]
        assert final_msg.role == "ASSISTANT"
        assert "successfully created" in final_msg.text

        # THEN the ComposioService was called correctly
        mock_service_class.assert_called_once_with(api_key="test_api_key_123")
        mock_service_instance.execute_tool.assert_called_once_with(
            tool_name="GITHUB_CREATE_AN_ISSUE",
            arguments={
                "owner": "test-owner",
                "repo": "test-repo",
                "title": "Bug in authentication",
                "body": "There seems to be an issue with login functionality",
            },
        )


def test_run_workflow__missing_api_key_raises_exception(vellum_adhoc_prompt_client, monkeypatch):
    """
    Test that ComposioNode raises a proper exception when no API key is found in environment variables.
    """

    # Clear all potential API key environment variables
    monkeypatch.delenv("COMPOSIO_API_KEY", raising=False)
    monkeypatch.delenv("COMPOSIO_KEY", raising=False)

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        expected_outputs = [
            FunctionCallVellumValue(
                value=FunctionCall(
                    arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                    id="call_composio_test",
                    name="github_create_an_issue",
                    state="FULFILLED",
                ),
            ),
        ]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # GIVEN a Composio tool calling workflow
    workflow = BasicToolCallingNodeWithComposioToolWorkflow()

    # WHEN the workflow is executed without API key
    terminal_event = workflow.run(Inputs(query="Create a test issue"))

    # THEN the workflow should be rejected with an appropriate error message
    assert terminal_event.name == "workflow.execution.rejected"
    assert "No Composio API key found" in str(terminal_event.error.message)
    assert "COMPOSIO_API_KEY" in str(terminal_event.error.message)
    assert "COMPOSIO_KEY" in str(terminal_event.error.message)


def test_run_workflow__composio_api_key_precedence(vellum_adhoc_prompt_client, monkeypatch):
    """
    Test that COMPOSIO_API_KEY takes precedence over COMPOSIO_KEY when both are set.
    """

    # Set both environment variables
    monkeypatch.setenv("COMPOSIO_API_KEY", "primary_key")
    monkeypatch.setenv("COMPOSIO_KEY", "secondary_key")

    mock_composio_result = {"success": True}

    with mock.patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service_class:
        mock_service_instance = mock.Mock()
        mock_service_instance.execute_tool.return_value = mock_composio_result
        mock_service_class.return_value = mock_service_instance

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                        id="call_composio_test",
                        name="github_create_an_issue",
                        state="FULFILLED",
                    ),
                ),
            ]

            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        # GIVEN a workflow and both API keys set
        workflow = BasicToolCallingNodeWithComposioToolWorkflow()

        # WHEN the workflow runs (we don't need the full execution, just need to trigger ComposioService creation)
        try:
            workflow.run(Inputs(query="Create a test issue"))
        except Exception:
            pass  # We don't care about the full execution, just the API key selection

        # THEN ComposioService should be called with the primary key (COMPOSIO_API_KEY)
        mock_service_class.assert_called_with(api_key="primary_key")


def test_run_workflow__composio_key_fallback(vellum_adhoc_prompt_client, monkeypatch):
    """
    Test that COMPOSIO_KEY is used when COMPOSIO_API_KEY is not set.
    """

    # Set only the fallback key
    monkeypatch.delenv("COMPOSIO_API_KEY", raising=False)
    monkeypatch.setenv("COMPOSIO_KEY", "fallback_key")

    mock_composio_result = {"success": True}

    with mock.patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service_class:
        mock_service_instance = mock.Mock()
        mock_service_instance.execute_tool.return_value = mock_composio_result
        mock_service_class.return_value = mock_service_instance

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                        id="call_composio_test",
                        name="github_create_an_issue",
                        state="FULFILLED",
                    ),
                ),
            ]

            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        # GIVEN a workflow with only fallback key set
        workflow = BasicToolCallingNodeWithComposioToolWorkflow()

        # WHEN the workflow runs
        try:
            workflow.run(Inputs(query="Create a test issue"))
        except Exception:
            pass  # We don't care about the full execution, just the API key selection

        # THEN ComposioService should be called with the fallback key
        mock_service_class.assert_called_with(api_key="fallback_key")


def test_run_workflow__composio_tool_execution_error(vellum_adhoc_prompt_client, monkeypatch):
    """
    Test that ComposioNode properly handles and re-raises exceptions from ComposioService.
    """

    monkeypatch.setenv("COMPOSIO_API_KEY", "test_api_key")

    with mock.patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService") as mock_service_class:
        mock_service_instance = mock.Mock()
        # Simulate an API error
        mock_service_instance.execute_tool.side_effect = Exception("API rate limit exceeded")
        mock_service_class.return_value = mock_service_instance

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                        id="call_composio_error_test",
                        name="github_create_an_issue",
                        state="FULFILLED",
                    ),
                ),
            ]

            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        # GIVEN a workflow and ComposioService that will fail
        workflow = BasicToolCallingNodeWithComposioToolWorkflow()

        # WHEN the workflow is executed
        terminal_event = workflow.run(Inputs(query="Create a test issue"))

        # THEN the workflow should be rejected with the original error context
        assert terminal_event.name == "workflow.execution.rejected"
        assert "Error executing Composio tool 'GITHUB_CREATE_AN_ISSUE'" in str(terminal_event.error.message)
        assert "API rate limit exceeded" in str(terminal_event.error.message)


def test_tool_name_mapping_from_composio_definition():
    """
    Test that the ComposioToolDefinition.name property correctly maps action names to function names.
    """

    # GIVEN a ComposioToolDefinition
    tool = github_create_issue_tool

    # WHEN we access the name property
    function_name = tool.name

    # THEN it should be the lowercase version of the action
    assert function_name == "github_create_an_issue"
    assert function_name == tool.action.lower()


def test_workflow_prompt_structure_includes_composio_tool_as_function(vellum_adhoc_prompt_client, monkeypatch):
    """
    Test that the workflow properly includes the ComposioToolDefinition as a function in the prompt calls.
    """

    monkeypatch.setenv("COMPOSIO_API_KEY", "test_api_key")

    with mock.patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.ComposioService"):

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs = [StringVellumValue(value="No function call needed")]

            events: List[ExecutePromptEvent] = [
                InitiatedExecutePromptEvent(execution_id=execution_id),
                FulfilledExecutePromptEvent(
                    execution_id=execution_id,
                    outputs=expected_outputs,
                ),
            ]
            yield from events

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

        # GIVEN a workflow
        workflow = BasicToolCallingNodeWithComposioToolWorkflow()

        # WHEN the workflow runs
        workflow.run(Inputs(query="What can you help me with?"))

        # THEN the prompt call should include our ComposioToolDefinition as a function
        call_args = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
        functions = call_args.kwargs["functions"]

        assert len(functions) == 1
        function_def = functions[0]
        assert isinstance(function_def, FunctionDefinition)
        assert function_def.name == "github_create_an_issue"  # Should use the tool's name property
        assert (
            function_def.description == "Create a new issue in a GitHub repository"
        )  # Should use the tool's description
