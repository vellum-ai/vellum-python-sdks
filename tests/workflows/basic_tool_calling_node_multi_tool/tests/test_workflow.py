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

from tests.workflows.basic_tool_calling_node_multi_tool.workflow import BasicToolCallingNodeMultiToolWorkflow


def test_get_current_weather_workflow(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Test that the GetCurrentWeatherWorkflow returns the expected outputs.
    """

    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"location": "San Francisco", "unit": "celsius"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="get_current_weather",
                        state="FULFILLED",
                    ),
                ),
            ]
        elif call_count == 2:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={
                            "answer": "The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."  # noqa: E501
                        },
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="format_answer",
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

    # Set up the mock to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    uuid4_generator = mock_uuid4_generator("vellum.workflows.nodes.displayable.bases.inline_prompt_node.node.uuid4")
    first_call_input_id = uuid4_generator()
    first_call_input_id_2 = uuid4_generator()
    second_call_input_id = uuid4_generator()
    second_call_input_id_2 = uuid4_generator()
    third_call_input_id = uuid4_generator()
    third_call_input_id_2 = uuid4_generator()

    # GIVEN a get current weather workflow
    workflow = BasicToolCallingNodeMultiToolWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run()

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
                    name="get_current_weather",
                    arguments={"location": "San Francisco", "unit": "celsius"},
                    id="call_7115tNTmEACTsQRGwKpJipJK",
                ),
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text=None,
            role="ASSISTANT",
            content=FunctionCallChatMessageContent(
                type="FUNCTION_CALL",
                value=FunctionCallChatMessageContentValue(
                    name="format_answer",
                    arguments={
                        "answer": "The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."  # noqa: E501
                    },
                    id="call_7115tNTmEACTsQRGwKpJipJK",
                ),
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text=None,
            role="FUNCTION",
            content=StringChatMessageContent(
                type="STRING",
                value='"The answer is: The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',  # noqa: E501
            ),
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
        ChatMessage(
            text="Based on the function call, the current temperature in San Francisco is 70 degrees celsius.",
            role="ASSISTANT",
            content=None,
            source="call_7115tNTmEACTsQRGwKpJipJK",
        ),
    ]

    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    assert first_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(key="question", type="STRING", value="What's the weather like in San Francisco?"),
            PromptRequestJsonInput(
                key="chat_history",
                type="JSON",
                value=[],
            ),
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
                                block_type="PLAIN_TEXT", state=None, cache_config=None, text="You are a weather expert"
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
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="get_current_weather",
                description="\n    Get the current weather in a given location.\n    ",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}, "unit": {"type": "string"}},
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="format_answer",
                description=None,
                parameters={"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]},
                forced=None,
                strict=None,
            ),
        ],
        "expand_meta": None,
        "request_options": mock.ANY,
    }

    second_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[1]
    assert second_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(key="question", type="STRING", value="What's the weather like in San Francisco?"),
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
                                name="get_current_weather",
                                arguments={"location": "San Francisco", "unit": "celsius"},
                                id="call_7115tNTmEACTsQRGwKpJipJK",
                            ),
                        ),
                    ),
                    ChatMessage(
                        text=None,
                        role="FUNCTION",
                        content=StringChatMessageContent(
                            type="STRING",
                            value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',  # noqa: E501
                        ),
                        source="call_7115tNTmEACTsQRGwKpJipJK",
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
                                block_type="PLAIN_TEXT", state=None, cache_config=None, text="You are a weather expert"
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
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="get_current_weather",
                description="\n    Get the current weather in a given location.\n    ",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}, "unit": {"type": "string"}},
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="format_answer",
                description=None,
                parameters={"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]},
                forced=None,
                strict=None,
            ),
        ],
        "expand_meta": None,
        "request_options": mock.ANY,
    }

    third_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[2]
    assert third_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(key="question", type="STRING", value="What's the weather like in San Francisco?"),
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
                                name="get_current_weather",
                                arguments={"location": "San Francisco", "unit": "celsius"},
                                id="call_7115tNTmEACTsQRGwKpJipJK",
                            ),
                        ),
                        source="call_7115tNTmEACTsQRGwKpJipJK",
                    ),
                    ChatMessage(
                        text=None,
                        role="FUNCTION",
                        content=StringChatMessageContent(
                            type="STRING",
                            value='"The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',  # noqa: E501
                        ),
                        source="call_7115tNTmEACTsQRGwKpJipJK",
                    ),
                    ChatMessage(
                        text=None,
                        role="ASSISTANT",
                        content=FunctionCallChatMessageContent(
                            type="FUNCTION_CALL",
                            value=FunctionCallChatMessageContentValue(
                                name="format_answer",
                                arguments={
                                    "answer": "The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."  # noqa: E501
                                },
                                id="call_7115tNTmEACTsQRGwKpJipJK",
                            ),
                        ),
                        source="call_7115tNTmEACTsQRGwKpJipJK",
                    ),
                    ChatMessage(
                        text=None,
                        role="FUNCTION",
                        content=StringChatMessageContent(
                            type="STRING",
                            value='"The answer is: The current weather in San Francisco is sunny with a temperature of 70 degrees celsius."',  # noqa: E501
                        ),
                        source="call_7115tNTmEACTsQRGwKpJipJK",
                    ),
                ],
            ),
        ],
        "input_variables": [
            VellumVariable(
                id=str(third_call_input_id),
                key="question",
                type="STRING",
                required=None,
                default=None,
                extensions=None,
            ),
            VellumVariable(
                id=str(third_call_input_id_2),
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
                                block_type="PLAIN_TEXT", state=None, cache_config=None, text="You are a weather expert"
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
            VariablePromptBlock(block_type="VARIABLE", state=None, cache_config=None, input_variable="chat_history"),
        ],
        "settings": None,
        "functions": [
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="get_current_weather",
                description="\n    Get the current weather in a given location.\n    ",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}, "unit": {"type": "string"}},
                    "required": ["location", "unit"],
                },
                forced=None,
                strict=None,
            ),
            FunctionDefinition(
                state=None,
                cache_config=None,
                name="format_answer",
                description=None,
                parameters={"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]},
                forced=None,
                strict=None,
            ),
        ],
        "expand_meta": None,
        "request_options": mock.ANY,
    }
