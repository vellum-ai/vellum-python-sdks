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
from vellum.workflows.nodes.displayable.bases.inline_prompt_node.constants import DEFAULT_PROMPT_PARAMETERS

from tests.workflows.basic_tool_calling_node_inline_workflow.workflow import (
    BasicToolCallingNodeInlineWorkflowWorkflow,
    WorkflowInputs,
)


def test_tool_calling_node_inline_subworkflow(vellum_adhoc_prompt_client, mock_uuid4_generator):
    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"city": "San Francisco", "date": "2025-01-01"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="basic_inline_subworkflow_workflow",
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

    # GIVEN a workflow that combines tool calling with a subworkflow
    workflow = BasicToolCallingNodeInlineWorkflowWorkflow()

    # WHEN the workflow is executed
    terminal_event = workflow.run(
        inputs=WorkflowInputs(
            query="What's the weather like in San Francisco?",
        )
    )

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
                    name="basic_inline_subworkflow_workflow",
                    arguments={"city": "San Francisco", "date": "2025-01-01"},
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
                value='{"temperature": 70, "reasoning": "The weather in San Francisco on 2025-01-01 was hot"}',
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

    # AND the prompt was called with the correct parameters
    first_call = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0]
    assert first_call.kwargs == {
        "ml_model": "gpt-4o-mini",
        "input_values": [
            PromptRequestStringInput(key="question", type="STRING", value="What's the weather like in San Francisco?"),
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
                name="basic_inline_subworkflow_workflow",
                description="\n    A workflow that gets the weather for a given city and date.\n    ",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}, "date": {"type": "string"}},
                    "required": ["city", "date"],
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
                                name="basic_inline_subworkflow_workflow",
                                arguments={"city": "San Francisco", "date": "2025-01-01"},
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
                            value='{"temperature": 70, "reasoning": "The weather in San Francisco on 2025-01-01 was hot"}',  # noqa: E501
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
                name="basic_inline_subworkflow_workflow",
                description="\n    A workflow that gets the weather for a given city and date.\n    ",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}, "date": {"type": "string"}},
                    "required": ["city", "date"],
                },
                forced=None,
                strict=None,
            )
        ],
        "expand_meta": None,
        "request_options": mock.ANY,
    }


def test_workflow_stream_initiated_events(vellum_adhoc_prompt_client, mock_uuid4_generator):
    """
    Tests that streaming the workflow generates exactly 3 workflow.execution.initiated events.
    """

    def generate_prompt_events(*args, **kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())

        call_count = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count
        expected_outputs: List[PromptOutput]
        if call_count == 1:
            expected_outputs = [
                FunctionCallVellumValue(
                    value=FunctionCall(
                        arguments={"city": "San Francisco", "date": "2025-01-01"},
                        id="call_7115tNTmEACTsQRGwKpJipJK",
                        name="basic_inline_subworkflow_workflow",
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

    # GIVEN a workflow that combines tool calling with a subworkflow
    workflow = BasicToolCallingNodeInlineWorkflowWorkflow()

    # AND the mock is set up to return our events
    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    # WHEN the workflow is streamed
    stream = workflow.stream(
        inputs=WorkflowInputs(
            query="What's the weather like in San Francisco?",
        )
    )
    events = list(stream)

    workflow_initiated_events = [e for e in events if e.name == "workflow.execution.initiated"]
    assert len(workflow_initiated_events) == 3
