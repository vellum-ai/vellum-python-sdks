from unittest import mock
from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.chat_message import ChatMessage
from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_chat_message_content import FunctionCallChatMessageContent
from vellum.client.types.function_call_chat_message_content_value import FunctionCallChatMessageContentValue
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.function_definition import FunctionDefinition
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_request_chat_history_input import PromptRequestChatHistoryInput
from vellum.client.types.prompt_request_json_input import PromptRequestJsonInput
from vellum.client.types.prompt_request_string_input import PromptRequestStringInput
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.string_chat_message_content import StringChatMessageContent
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.variable_prompt_block import VariablePromptBlock
from vellum.client.types.vellum_variable import VellumVariable
from vellum.prompts.constants import DEFAULT_PROMPT_PARAMETERS
from vellum.workflows.constants import AuthorizationType
from vellum.workflows.types.definition import MCPServer, MCPToolDefinition

from tests.workflows.basic_tool_calling_node_mcp_tool.workflow import BasicToolCallingNodeWorkflowMCPTool, Inputs


def test_run_workflow__happy_path(vellum_adhoc_prompt_client, mock_uuid4_generator, monkeypatch):
    with mock.patch("vellum.workflows.nodes.displayable.tool_calling_node.utils.MCPService") as mock_mcp_service:
        mock_service_instance = mock.Mock()
        mock_service_instance.execute_tool.return_value = {
            "content": [
                {
                    "type": "text",
                    "text": '{"id":1028555060,"name":"new_test_repo"}',
                }
            ]
        }
        mock_service_instance.hydrate_tool_definitions.return_value = [
            MCPToolDefinition(
                name="create_repository",
                server=MCPServer(
                    name="github",
                    url="https://api.githubcopilot.com/mcp/",
                    authorization_type=AuthorizationType.BEARER_TOKEN,
                    bearer_token_value="github_pat_some_token",
                    api_key_header_key=None,
                    api_key_header_value=None,
                ),
                description="Create a new GitHub repository in your account",
                parameters={
                    "properties": {
                        "autoInit": {"description": "Initialize with README", "type": "boolean"},
                        "description": {"description": "Repository description", "type": "string"},
                        "name": {"description": "Repository name", "type": "string"},
                        "private": {"description": "Whether repo should be private", "type": "boolean"},
                    },
                    "required": ["name"],
                    "type": "object",
                },
            )
        ]
        mock_mcp_service.return_value = mock_service_instance

        # Set the required environment variable
        monkeypatch.setenv("GITHUB_PERSONAL_ACCESS_TOKEN", "test_github_token_123")

        def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
            execution_id = str(uuid4())

            call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
            expected_outputs: List[PromptOutput]
            if call_count == 1:
                expected_outputs = [
                    FunctionCallVellumValue(
                        value=FunctionCall(
                            arguments={"name": "new_test_repo", "autoInit": True},
                            id="call_7115tNTmEACTsQRGwKpJipJK",
                            name="github__create_repository",
                            state="FULFILLED",
                        ),
                    ),
                ]
            else:
                expected_outputs = [
                    StringVellumValue(value="The repository new_test_repo has been successfully created.")
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

        uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
        first_call_input_id = uuid4_generator()
        first_call_input_id_2 = uuid4_generator()
        second_call_input_id = uuid4_generator()
        second_call_input_id_2 = uuid4_generator()

        # GIVEN a repository creation workflow
        workflow = BasicToolCallingNodeWorkflowMCPTool()

        # WHEN the workflow is executed
        terminal_event = workflow.run(Inputs(query="Create a new test repository named new_test_repo"))

        # THEN the workflow is executed successfully
        assert terminal_event.name == "workflow.execution.fulfilled"

        assert terminal_event.outputs.text == "The repository new_test_repo has been successfully created."
        assert terminal_event.outputs.chat_history == [
            ChatMessage(
                text=None,
                role="ASSISTANT",
                content=FunctionCallChatMessageContent(
                    type="FUNCTION_CALL",
                    value=FunctionCallChatMessageContentValue(
                        name="github__create_repository",
                        arguments={"name": "new_test_repo", "autoInit": True},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                    ),
                ),
                source=None,
            ),
            ChatMessage(
                text=None,
                role="FUNCTION",
                content=StringChatMessageContent(
                    type="STRING",
                    value='{"content": [{"type": "text", "text": "{\\"id\\":1028555060,\\"name\\":\\"new_test_repo\\"}"}]}',  # noqa: E501
                ),
                source=None,
            ),
            ChatMessage(
                text="The repository new_test_repo has been successfully created.",
                role="ASSISTANT",
                content=None,
                source=None,
            ),
        ]

        first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
        assert first_call.kwargs == {
            "ml_model": "gpt-4o-mini",
            "input_values": [
                PromptRequestStringInput(
                    key="question", type="STRING", value="Create a new test repository named new_test_repo"
                ),
                PromptRequestJsonInput(key="chat_history", type="JSON", value=[]),
            ],
            "input_variables": [
                VellumVariable(
                    id=str(first_call_input_id),
                    key="question",
                    type="STRING",
                    required=None,
                    default=None,
                    extensions=None,
                ),
                VellumVariable(
                    id=str(first_call_input_id_2),
                    key="chat_history",
                    type="JSON",
                    required=None,
                    default=None,
                    extensions=None,
                ),
            ],
            "parameters": DEFAULT_PROMPT_PARAMETERS,
            "blocks": [
                ChatMessagePromptBlock(
                    block_type="CHAT_MESSAGE",
                    state=None,
                    cache_config=None,
                    chat_role="SYSTEM",
                    chat_source=None,
                    chat_message_unterminated=None,
                    blocks=[
                        RichTextPromptBlock(
                            block_type="RICH_TEXT",
                            state=None,
                            cache_config=None,
                            blocks=[
                                PlainTextPromptBlock(
                                    block_type="PLAIN_TEXT",
                                    state=None,
                                    cache_config=None,
                                    text="You are a helpful assistant",
                                )
                            ],
                        )
                    ],
                ),
                ChatMessagePromptBlock(
                    block_type="CHAT_MESSAGE",
                    state=None,
                    cache_config=None,
                    chat_role="USER",
                    chat_source=None,
                    chat_message_unterminated=None,
                    blocks=[
                        RichTextPromptBlock(
                            block_type="RICH_TEXT",
                            state=None,
                            cache_config=None,
                            blocks=[
                                VariablePromptBlock(
                                    block_type="VARIABLE", state=None, cache_config=None, input_variable="question"
                                )
                            ],
                        )
                    ],
                ),
                VariablePromptBlock(
                    block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"
                ),
            ],
            "settings": None,
            "functions": [
                FunctionDefinition(
                    state=None,
                    cache_config=None,
                    name="github__create_repository",
                    description="Create a new GitHub repository in your account",
                    parameters={
                        "type": "object",
                        "properties": {
                            "autoInit": {"description": "Initialize with README", "type": "boolean"},
                            "description": {"description": "Repository description", "type": "string"},
                            "name": {"description": "Repository name", "type": "string"},
                            "private": {"description": "Whether repo should be private", "type": "boolean"},
                        },
                        "required": ["name"],
                    },
                    forced=None,
                    strict=None,
                )
            ],
            "expand_meta": None,
            "request_options": mock.ANY,
        }

        # AND the MCP service was called correctly for tool execution
        mock_service_instance.execute_tool.assert_called_once_with(
            tool_def=MCPToolDefinition(
                name="create_repository",
                server=MCPServer(
                    name="github",
                    url="https://api.githubcopilot.com/mcp/",
                    authorization_type=AuthorizationType.BEARER_TOKEN,
                    bearer_token_value="github_pat_some_token",
                    api_key_header_key=None,
                    api_key_header_value=None,
                ),
                description="Create a new GitHub repository in your account",
                parameters={
                    "properties": {
                        "autoInit": {"description": "Initialize with README", "type": "boolean"},
                        "description": {"description": "Repository description", "type": "string"},
                        "name": {"description": "Repository name", "type": "string"},
                        "private": {"description": "Whether repo should be private", "type": "boolean"},
                    },
                    "required": ["name"],
                    "type": "object",
                },
            ),
            arguments={"name": "new_test_repo", "autoInit": True},
        )

        second_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[1]
        assert second_call.kwargs == {
            "ml_model": "gpt-4o-mini",
            "input_values": [
                PromptRequestStringInput(
                    key="question", type="STRING", value="Create a new test repository named new_test_repo"
                ),
                PromptRequestChatHistoryInput(
                    key="chat_history",
                    type="CHAT_HISTORY",
                    value=[
                        ChatMessage(
                            text=None,
                            role="ASSISTANT",
                            content=FunctionCallChatMessageContent(
                                type="FUNCTION_CALL",
                                value=FunctionCallChatMessageContentValue(
                                    name="github__create_repository",
                                    arguments={"name": "new_test_repo", "autoInit": True},
                                    id="call_7115tNTmEACTsQRGwKpJipJK",
                                ),
                            ),
                            source=None,
                        ),
                        ChatMessage(
                            text=None,
                            role="FUNCTION",
                            content=StringChatMessageContent(
                                type="STRING",
                                value='{"content": [{"type": "text", "text": "{\\"id\\":1028555060,\\"name\\":\\"new_test_repo\\"}"}]}',  # noqa: E501
                            ),
                            source=None,
                        ),
                    ],
                ),
            ],
            "input_variables": [
                VellumVariable(
                    id=str(second_call_input_id),
                    key="question",
                    type="STRING",
                    required=None,
                    default=None,
                    extensions=None,
                ),
                VellumVariable(
                    id=str(second_call_input_id_2),
                    key="chat_history",
                    type="CHAT_HISTORY",
                    required=None,
                    default=None,
                    extensions=None,
                ),
            ],
            "parameters": DEFAULT_PROMPT_PARAMETERS,
            "blocks": [
                ChatMessagePromptBlock(
                    block_type="CHAT_MESSAGE",
                    state=None,
                    cache_config=None,
                    chat_role="SYSTEM",
                    chat_source=None,
                    chat_message_unterminated=None,
                    blocks=[
                        RichTextPromptBlock(
                            block_type="RICH_TEXT",
                            state=None,
                            cache_config=None,
                            blocks=[
                                PlainTextPromptBlock(
                                    block_type="PLAIN_TEXT",
                                    state=None,
                                    cache_config=None,
                                    text="You are a helpful assistant",
                                )
                            ],
                        )
                    ],
                ),
                ChatMessagePromptBlock(
                    block_type="CHAT_MESSAGE",
                    state=None,
                    cache_config=None,
                    chat_role="USER",
                    chat_source=None,
                    chat_message_unterminated=None,
                    blocks=[
                        RichTextPromptBlock(
                            block_type="RICH_TEXT",
                            state=None,
                            cache_config=None,
                            blocks=[
                                VariablePromptBlock(
                                    block_type="VARIABLE", state=None, cache_config=None, input_variable="question"
                                )
                            ],
                        )
                    ],
                ),
                VariablePromptBlock(
                    block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"
                ),
            ],
            "settings": None,
            "functions": [
                FunctionDefinition(
                    state=None,
                    cache_config=None,
                    name="github__create_repository",
                    description="Create a new GitHub repository in your account",
                    parameters={
                        "type": "object",
                        "properties": {
                            "autoInit": {"description": "Initialize with README", "type": "boolean"},
                            "description": {"description": "Repository description", "type": "string"},
                            "name": {"description": "Repository name", "type": "string"},
                            "private": {"description": "Whether repo should be private", "type": "boolean"},
                        },
                        "required": ["name"],
                    },
                    forced=None,
                    strict=None,
                )
            ],
            "expand_meta": None,
            "request_options": mock.ANY,
        }
