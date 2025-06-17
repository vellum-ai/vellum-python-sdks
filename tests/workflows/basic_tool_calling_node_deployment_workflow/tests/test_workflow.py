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
from vellum.client.types.workflow_deployment_release import WorkflowDeploymentRelease
from vellum.client.types.workflow_execution_workflow_result_event import WorkflowExecutionWorkflowResultEvent
from vellum.client.types.workflow_output_string import WorkflowOutputString
from vellum.client.types.workflow_request_string_input_request import WorkflowRequestStringInputRequest
from vellum.client.types.workflow_result_event import WorkflowResultEvent
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.basic_tool_calling_node_deployment_workflow.workflow import (
    BasicToolCallingNodeDeploymentWorkflowWorkflow,
    Inputs,
)


def test_get_current_weather_workflow(vellum_adhoc_prompt_client, vellum_client, mock_uuid4_generator):
    """
    Test that the GetCurrentWeatherWorkflow returns the expected outputs.
    """

    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:  # noqa: U100
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Francisco", "unit": "celsius"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="deployment_1",
                        state="FULFILLED",
                    ),
                ),
            ]
        else:
            expected_outputs = [
                StringVellumValue(
                    value="Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
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

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    mock_workflow_deployment_release = WorkflowDeploymentRelease(
        id="mock-deployment-id",
        created="2024-01-01T00:00:00Z",
        environment={"id": "mock-env-id", "name": "mock-env-name", "label": "mock-env-label"},
        created_by={"id": "mock-user-id", "email": "mock@example.com"},
        workflow_version={
            "id": "mock-version-id",
            "input_variables": [
                {"id": "location-input-id", "key": "location", "type": "STRING", "required": True, "default": None},
                {"id": "unit-input-id", "key": "unit", "type": "STRING", "required": True, "default": None},
            ],
            "output_variables": [],
        },
        deployment={"name": "deployment_1"},
        release_tags=[],
        reviews=[],
    )
    vellum_client.release_reviews.retrieve_workflow_deployment_release.return_value = mock_workflow_deployment_release

    def mock_workflow_execution(*args, **kwargs):  # noqa: U100
        yield WorkflowExecutionWorkflowResultEvent(
            execution_id="mock-execution-id",
            type="WORKFLOW",
            data=WorkflowResultEvent(id="mock-event-id", state="INITIATED", ts="2024-01-01T00:00:00Z"),
        )
        yield WorkflowExecutionWorkflowResultEvent(
            execution_id="mock-execution-id",
            type="WORKFLOW",
            data=WorkflowResultEvent(
                id="mock-event-id",
                state="FULFILLED",
                ts="2024-01-01T00:00:00Z",
                outputs=[
                    WorkflowOutputString(
                        id="mock-output-id",
                        name="mock-output-name",
                        type="STRING",
                        value="The current weather in San Francisco is sunny with a temperature of 70 degrees celsius.",
                    )
                ],
            ),
        )

    vellum_client.execute_workflow_stream.side_effect = mock_workflow_execution

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    first_call_input_id = uuid4_generator()
    first_call_input_id_2 = uuid4_generator()
    second_call_input_id = uuid4_generator()
    second_call_input_id_2 = uuid4_generator()

    # GIVEN a get current weather workflow
    workflow = BasicToolCallingNodeDeploymentWorkflowWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run(Inputs(query="What's the weather like in San Francisco?"))

    # THEN the workflow is executed successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert (
        terminal_event.outputs.text
        == "Based on the function call, the current temperature in San Francisco is 70 degrees celsius."
    )

    assert terminal_event.outputs.chat_history == [
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="deployment_1",
                    arguments={"location": "San Francisco", "unit": "celsius"},
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
                value='{"mock_output_name": "The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."}',  # noqa: E501
            ),
            source=None,
        ),
        ChatMessage(
            text="Based on the function call, the current temperature in San Francisco is 70 degrees celsius.",
            role="ASSISTANT",
            content=None,
            source=None,
        ),
    ]

    vellum_client.execute_workflow_stream.assert_called_once()
    call_args = vellum_client.execute_workflow_stream.call_args
    assert call_args.kwargs == {
        "inputs": [
            WorkflowRequestStringInputRequest(name="location", type="STRING", value="San Francisco"),
            WorkflowRequestStringInputRequest(name="unit", type="STRING", value="celsius"),
        ],
        "workflow_deployment_id": None,
        "workflow_deployment_name": "deployment_1",
        "release_tag": "latest",
        "external_id": Ellipsis,
        "event_types": ["WORKFLOW"],
        "metadata": Ellipsis,
        "request_options": mock.ANY,
    }

    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    assert first_call.kwargs == {
        "ml_model": "gpt-4",
        "input_values": [
            PromptRequestStringInput(key="query", type="STRING", value="What's the weather like in San Francisco?"),
            PromptRequestJsonInput(key="chat_history", type="JSON", value=[]),
        ],
        "input_variables": [
            VellumVariable(
                id=str(first_call_input_id),
                key="query",
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
                                text="You are a helpful assistant. Use the available tools to help the user.",
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
                                block_type="VARIABLE", state=None, cache_config=None, input_variable="query"
                            )
                        ],
                    )
                ],
            ),
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="deployment_1",
                description=None,
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}, "unit": {"type": "string"}},
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            )
        ],
        "expand_meta": None,
        "request_options": mock.ANY,
    }

    second_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[1]
    assert second_call.kwargs == {
        "ml_model": "gpt-4",
        "input_values": [
            PromptRequestStringInput(key="query", type="STRING", value="What's the weather like in San Francisco?"),
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
                                name="deployment_1",
                                arguments={"location": "San Francisco", "unit": "celsius"},
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
                            value='{"mock_output_name": "The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."}',  # noqa: E501
                        ),
                        source=None,
                    ),
                ],
            ),
        ],
        "input_variables": [
            VellumVariable(
                id=str(second_call_input_id),
                key="query",
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
                                text="You are a helpful assistant. Use the available tools to help the user.",
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
                                block_type="VARIABLE", state=None, cache_config=None, input_variable="query"
                            )
                        ],
                    )
                ],
            ),
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="deployment_1",
                description=None,
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}, "unit": {"type": "string"}},
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            )
        ],
        "expand_meta": None,
        "request_options": mock.ANY,
    }
