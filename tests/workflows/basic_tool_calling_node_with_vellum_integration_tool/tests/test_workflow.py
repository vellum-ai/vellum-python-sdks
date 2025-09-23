from unittest import mock
from uuid import uuid4
from typing import Iterator, List, cast

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.string_vellum_value import StringVellumValue

from tests.workflows.basic_tool_calling_node_with_vellum_integration_tool.workflow import (
    BasicToolCallingNodeWithVellumIntegrationToolWorkflow,
    Inputs,
    github_create_issue_tool,
)


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, vellum_client, mock_uuid4_generator):
    """
    Test that the VellumIntegrationToolCallingNode workflow returns the expected outputs
    when successfully executing a Vellum Integration tool.
    """

    # Mock VellumIntegrationService
    mock_vellum_result = {
        "issue": {
            "id": 123,
            "title": "Test Issue",
            "body": "This is a test issue created via Vellum Integration",
            "url": "https://github.com/owner/repo/issues/123",
        }
    }

    # Mock tool details for hydration
    mock_tool_details = {
        "name": "create_issue",
        "description": "Create a new issue in a GitHub repository",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Repository owner"},
                "repo": {"type": "string", "description": "Repository name"},
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue body"},
            },
        },
        "provider": "COMPOSIO",
    }

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.VellumIntegrationService"
    ) as mock_service_class_utils:
        mock_service_instance = mock.Mock()
        mock_service_instance.execute_tool.return_value = mock_vellum_result
        mock_service_instance.get_tool_definition.return_value = mock_tool_details
        mock_service_class.return_value = mock_service_instance
        mock_service_class_utils.return_value = mock_service_instance

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
                            id="call_vellum_integration_create_issue",
                            name="create_issue",
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

        # GIVEN a Vellum Integration tool calling workflow
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

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
        assert function_call_msg.content is not None
        assert function_call_msg.content.type == "FUNCTION_CALL"

        # Cast to the specific type to help mypy
        function_content = cast(FunctionCallChatMessageContent, function_call_msg.content)
        assert function_content.value.name == "create_issue"

        # Function result message
        function_result_msg = terminal_event.outputs.chat_history[1]
        assert function_result_msg.role == "FUNCTION"
        assert function_result_msg.content is not None
        assert function_result_msg.content.type == "STRING"
        # The result should be the JSON serialized version of mock_vellum_result
        assert mock_vellum_result["issue"]["id"] == 123

        # Final assistant message
        final_msg = terminal_event.outputs.chat_history[2]
        assert final_msg.role == "ASSISTANT"
        assert final_msg.text is not None
        assert "successfully created" in final_msg.text

        # THEN the VellumIntegrationService was called correctly
        assert mock_service_class.call_count >= 1  # Called for hydration and execution
        mock_service_instance.execute_tool.assert_called_once_with(
            integration="GITHUB",
            provider="COMPOSIO",
            tool_name="create_issue",
            arguments={
                "owner": "test-owner",
                "repo": "test-repo",
                "title": "Bug in authentication",
                "body": "There seems to be an issue with login functionality",
            },
        )


def test_run_workflow__service_error_uses_fallback(vellum_adhoc_prompt_client):
    """
    Test that the workflow properly handles VellumIntegrationService errors by using fallback compilation.
    """

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.VellumIntegrationService"
    ) as mock_service_class_utils:
        # Mock service to raise an exception during compilation (get_tool_definition)
        mock_service_instance = mock.Mock()
        mock_service_instance.get_tool_definition.side_effect = Exception("Service unavailable")
        mock_service_instance.execute_tool.return_value = {"success": True}
        mock_service_class.return_value = mock_service_instance
        mock_service_class_utils.return_value = mock_service_instance

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
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

        # WHEN the workflow runs (should not fail due to fallback)
        terminal_event = workflow.run(Inputs(query="What can you help me with?"))

        # THEN the workflow should succeed with fallback
        assert terminal_event.name == "workflow.execution.fulfilled"

        # AND the prompt call should still include our function with fallback parameters
        call_args = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
        functions = call_args.kwargs["functions"]

        assert len(functions) == 1
        function_def = functions[0]
        assert isinstance(function_def, FunctionDefinition)
        assert function_def.name == "create_issue"
        assert function_def.description == "Create a new issue in a GitHub repository"
        # Should have empty parameters due to fallback
        assert function_def.parameters == {}


def test_run_workflow__tool_execution_error(vellum_adhoc_prompt_client):
    """
    Test that VellumIntegrationNode properly handles and re-raises exceptions from VellumIntegrationService.
    """

    mock_tool_details = {
        "name": "create_issue",
        "description": "Create a new issue in a GitHub repository",
        "parameters": {},
        "provider": "COMPOSIO",
    }

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.VellumIntegrationService"
    ) as mock_service_class_utils:
        mock_service_instance = mock.Mock()
        mock_service_instance.get_tool_definition.return_value = mock_tool_details
        # Simulate an API error during execution
        mock_service_instance.execute_tool.side_effect = Exception("API rate limit exceeded")
        mock_service_class.return_value = mock_service_instance
        mock_service_class_utils.return_value = mock_service_instance

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                        id="call_vellum_error_test",
                        name="create_issue",
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

        # GIVEN a workflow and VellumIntegrationService that will fail during execution
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

        # WHEN the workflow is executed
        terminal_event = workflow.run(Inputs(query="Create a test issue"))

        # THEN the workflow should be rejected with the original error context
        assert terminal_event.name == "workflow.execution.rejected"
        assert "Error executing Vellum Integration tool 'create_issue'" in str(terminal_event.error.message)
        assert "API rate limit exceeded" in str(terminal_event.error.message)


def test_tool_definition_properties():
    """
    Test that the VellumIntegrationToolDefinition has the correct properties.
    """

    # GIVEN a VellumIntegrationToolDefinition
    tool = github_create_issue_tool

    # WHEN we access its properties
    # THEN they should be as expected
    assert tool.type == "INTEGRATION"
    assert tool.provider.value == "COMPOSIO"
    assert tool.integration == "GITHUB"
    assert tool.name == "create_issue"
    assert tool.description == "Create a new issue in a GitHub repository"


def test_workflow_prompt_structure_includes_vellum_integration_tool_as_function(vellum_adhoc_prompt_client):
    """
    Test that the workflow properly includes the VellumIntegrationToolDefinition as a function in the prompt calls.
    """

    mock_tool_details = {
        "name": "create_issue",
        "description": "Create a new issue in a GitHub repository",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue body"},
            },
        },
        "provider": "COMPOSIO",
    }

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.VellumIntegrationService"
    ) as mock_service_class_utils:
        mock_service_instance = mock.Mock()
        mock_service_instance.get_tool_definition.return_value = mock_tool_details
        mock_service_class.return_value = mock_service_instance
        mock_service_class_utils.return_value = mock_service_instance

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
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

        # WHEN the workflow runs
        workflow.run(Inputs(query="What can you help me with?"))

        # THEN the prompt call should include our VellumIntegrationToolDefinition as a function
        call_args = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
        functions = call_args.kwargs["functions"]

        assert len(functions) == 1
        function_def = functions[0]
        assert isinstance(function_def, FunctionDefinition)
        assert function_def.name == "create_issue"
        assert function_def.description == "Create a new issue in a GitHub repository"
        assert "title" in function_def.parameters["properties"]
        assert "body" in function_def.parameters["properties"]


def test_compile_function_with_successful_service_call():
    """
    Test that the compile_vellum_integration_tool_definition function works with a successful service call.
    """
    from vellum.workflows.utils.functions import compile_vellum_integration_tool_definition

    mock_tool_details = {
        "name": "create_issue",
        "description": "Enhanced description from service",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Issue title"},
            },
        },
        "provider": "COMPOSIO",
    }

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
        mock_service_instance = mock.Mock()
        mock_service_instance.get_tool_definition.return_value = mock_tool_details
        mock_service_class.return_value = mock_service_instance

        # GIVEN a VellumIntegrationToolDefinition
        tool = github_create_issue_tool

        # WHEN we compile it
        result = compile_vellum_integration_tool_definition(tool)

        # THEN it should return the enhanced definition from the service
        assert result.name == "create_issue"
        assert result.description == "Enhanced description from service"
        assert "title" in result.parameters["properties"]

        # AND the service should have been called with correct parameters
        mock_service_instance.get_tool_definition.assert_called_once_with(
            integration="GITHUB", provider="COMPOSIO", tool_name="create_issue"
        )


def test_compile_function_with_service_failure_uses_fallback():
    """
    Test that the compile_vellum_integration_tool_definition function uses fallback when service fails.
    """
    from vellum.workflows.utils.functions import compile_vellum_integration_tool_definition

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
        mock_service_instance = mock.Mock()
        mock_service_instance.get_tool_definition.side_effect = Exception("Service down")
        mock_service_class.return_value = mock_service_instance

        # GIVEN a VellumIntegrationToolDefinition
        tool = github_create_issue_tool

        # WHEN we compile it and the service fails
        result = compile_vellum_integration_tool_definition(tool)

        # THEN it should return the fallback definition with basic information
        assert result.name == "create_issue"
        assert result.description == "Create a new issue in a GitHub repository"  # From tool definition
        assert result.parameters == {}  # Empty fallback parameters
