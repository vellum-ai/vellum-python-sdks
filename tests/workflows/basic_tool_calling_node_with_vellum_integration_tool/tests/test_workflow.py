from unittest import mock
from uuid import uuid4
from typing import Iterator, List, Union, cast

from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.types.definition import VellumIntegrationToolDetails

from tests.workflows.basic_tool_calling_node_with_vellum_integration_tool.workflow import (
    BasicToolCallingNodeWithVellumIntegrationToolWorkflow,
    Inputs,
    github_create_issue_tool,
)


def _setup_mock_service(
    mock_service_class,
    mock_service_class_utils,
    tool_details=None,
    execute_result=None,
    get_tool_error=None,
    execute_error=None,
):
    """Helper to set up VellumIntegrationService mocks."""
    from vellum.workflows.constants import VellumIntegrationProviderType
    from vellum.workflows.types.definition import VellumIntegrationToolDetails

    mock_service_instance = mock.Mock()

    if get_tool_error:
        mock_service_instance.get_tool_definition.side_effect = get_tool_error
    elif tool_details:
        # Create proper VellumIntegrationToolDetails object from dict
        tool_details_obj = VellumIntegrationToolDetails(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration_name="GITHUB",
            name=tool_details.get("name", "create_issue"),
            description=tool_details.get("description", "Mock description"),
            parameters=tool_details.get("input_parameters", {}),
        )
        mock_service_instance.get_tool_definition.return_value = tool_details_obj

    if execute_error:
        mock_service_instance.execute_tool.side_effect = execute_error
    elif execute_result:
        mock_service_instance.execute_tool.return_value = execute_result

    mock_service_class.return_value = mock_service_instance
    mock_service_class_utils.return_value = mock_service_instance
    return mock_service_instance


def _generate_events(outputs, execution_id=None):
    """Helper to generate ExecutePromptEvents."""
    if execution_id is None:
        execution_id = str(uuid4())

    return [
        InitiatedExecutePromptEvent(execution_id=execution_id),
        FulfilledExecutePromptEvent(execution_id=execution_id, outputs=outputs),
    ]


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, vellum_client, mock_uuid4_generator):
    """Test successful tool execution with full workflow verification."""
    mock_vellum_result = {
        "issue": {"id": 123, "title": "Test Issue", "url": "https://github.com/owner/repo/issues/123"}
    }

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

        mock_service_instance = _setup_mock_service(
            mock_service_class,
            mock_service_class_utils,
            tool_details=mock_tool_details,
            execute_result=mock_vellum_result,
        )

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
            if call_count == 1:
                outputs: List[Union[FunctionCallVellumValue, StringVellumValue]] = [
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
                        )
                    )
                ]
            else:
                outputs = [
                    StringVellumValue(
                        value="I've successfully created the GitHub issue. "
                        "You can view it at: https://github.com/owner/repo/issues/123"
                    )
                ]

            yield from _generate_events(outputs)

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

        terminal_event = workflow.run(
            Inputs(query="Create an issue in the test-owner/test-repo repository about authentication bug")
        )

        assert terminal_event.name == "workflow.execution.fulfilled"
        assert "successfully created" in terminal_event.outputs.text
        assert len(terminal_event.outputs.chat_history) == 3

        # Verify function call message
        function_call_msg = terminal_event.outputs.chat_history[0]
        assert function_call_msg.role == "ASSISTANT"
        function_content = cast(FunctionCallChatMessageContent, function_call_msg.content)
        assert function_content.value.name == "create_issue"

        # Verify function result and final messages
        assert terminal_event.outputs.chat_history[1].role == "FUNCTION"
        assert terminal_event.outputs.chat_history[2].role == "ASSISTANT"

        # Verify service was called correctly
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


def test_run_workflow__error_handling_and_fallback(vellum_adhoc_prompt_client):
    """Test service errors use fallback and execution errors are properly raised."""
    # Test fallback when service unavailable
    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.VellumIntegrationService"
    ) as mock_service_class_utils:

        _setup_mock_service(
            mock_service_class, mock_service_class_utils, get_tool_error=Exception("Service unavailable")
        )

        def generate_fallback_events(*_args, **_kwargs):
            yield from _generate_events([StringVellumValue(value="No function call needed")])

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_fallback_events
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

        terminal_event = workflow.run(Inputs(query="What can you help me with?"))
        assert terminal_event.name == "workflow.execution.fulfilled"

        # Verify fallback function definition
        call_args = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
        functions = call_args.kwargs["functions"]
        assert len(functions) == 1
        function_def = functions[0]
        assert function_def.name == "create_issue"
        assert function_def.parameters == {}  # Empty due to fallback


def test_run_workflow__tool_execution_error(vellum_adhoc_prompt_client):
    """Test tool execution errors are properly handled and re-raised."""
    mock_tool_details = {
        "name": "create_issue",
        "description": "Create a new issue",
        "input_parameters": {},
        "provider": "COMPOSIO",
    }

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class, mock.patch(
        "vellum.workflows.nodes.displayable.tool_calling_node.utils.VellumIntegrationService"
    ) as mock_service_class_utils:

        _setup_mock_service(
            mock_service_class,
            mock_service_class_utils,
            tool_details=mock_tool_details,
            execute_error=Exception("API rate limit exceeded"),
        )

        def generate_error_events(*_args, **_kwargs):
            outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"owner": "test-owner", "repo": "test-repo", "title": "Test Issue"},
                        id="call_vellum_error_test",
                        name="create_issue",
                    )
                )
            ]
            yield from _generate_events(outputs)

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_error_events
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()

        terminal_event = workflow.run(Inputs(query="Create a test issue"))

        assert terminal_event.name == "workflow.execution.rejected"
        assert "Error executing Vellum Integration tool 'create_issue'" in str(terminal_event.error.message)
        assert "API rate limit exceeded" in str(terminal_event.error.message)


def test_tool_definition_and_function_compilation():
    """Test tool properties and function compilation with both success and failure scenarios."""
    # Test basic tool properties
    tool = github_create_issue_tool
    assert tool.type == "VELLUM_INTEGRATION"
    assert tool.provider.value == "COMPOSIO"
    assert tool.integration_name == "GITHUB"
    assert tool.name == "create_issue"
    assert tool.description == "Create a new issue in a GitHub repository"

    from vellum.workflows.utils.functions import compile_vellum_integration_tool_definition

    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
        mock_service_instance = mock.Mock()
        # Create a proper VellumIntegrationToolDetails object
        mock_tool_details_obj = VellumIntegrationToolDetails(
            provider=VellumIntegrationProviderType.COMPOSIO,
            integration_name="GITHUB",
            name="create_issue",
            description="Enhanced description from service",
            parameters={"type": "object", "properties": {"title": {"type": "string", "description": "Issue title"}}},
        )
        mock_service_instance.get_tool_definition.return_value = mock_tool_details_obj
        mock_service_class.return_value = mock_service_instance

        result = compile_vellum_integration_tool_definition(tool)
        assert result.name == "create_issue"
        assert result.description == "Enhanced description from service"
        assert result.parameters is not None and "properties" in result.parameters
        assert result.parameters["properties"] is not None and "title" in result.parameters["properties"]
        mock_service_instance.get_tool_definition.assert_called_once_with(
            integration="GITHUB", provider="COMPOSIO", tool_name="create_issue"
        )

    # Test fallback on service failure
    with mock.patch("vellum.workflows.utils.functions.VellumIntegrationService") as mock_service_class:
        mock_service_instance = mock.Mock()
        mock_service_instance.get_tool_definition.side_effect = Exception("Service down")
        mock_service_class.return_value = mock_service_instance

        result = compile_vellum_integration_tool_definition(tool)
        assert result.name == "create_issue"
        assert result.description == "Create a new issue in a GitHub repository"
        assert result.parameters == {}


def test_workflow_prompt_structure_with_function_definition(vellum_adhoc_prompt_client):
    """Test workflow includes VellumIntegrationToolDefinition correctly in prompt calls."""
    mock_tool_details = {
        "name": "create_issue",
        "description": "Create a new issue in a GitHub repository",
        "input_parameters": {
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

        _setup_mock_service(mock_service_class, mock_service_class_utils, tool_details=mock_tool_details)

        def generate_events(*_args, **_kwargs):
            yield from _generate_events([StringVellumValue(value="No function call needed")])

        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_events
        workflow = BasicToolCallingNodeWithVellumIntegrationToolWorkflow()
        workflow.run(Inputs(query="What can you help me with?"))

        call_args = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
        functions = call_args.kwargs["functions"]

        assert len(functions) == 1
        function_def = functions[0]
        assert isinstance(function_def, FunctionDefinition)
        assert function_def.name == "create_issue"
        assert function_def.description == "Create a new issue in a GitHub repository"
        assert function_def.parameters is not None and "properties" in function_def.parameters
        assert function_def.parameters["properties"] is not None and "title" in function_def.parameters["properties"]
        assert function_def.parameters["properties"] is not None and "body" in function_def.parameters["properties"]
