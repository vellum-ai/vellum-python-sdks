from uuid import uuid4
from typing import Iterator, List

from vellum.client.types.chat_message_prompt_block import ChatMessagePromptBlock
from vellum.client.types.execute_prompt_event import ExecutePromptEvent
from vellum.client.types.fulfilled_execute_prompt_event import FulfilledExecutePromptEvent
from vellum.client.types.initiated_execute_prompt_event import InitiatedExecutePromptEvent
from vellum.client.types.plain_text_prompt_block import PlainTextPromptBlock
from vellum.client.types.prompt_output import PromptOutput
from vellum.client.types.prompt_parameters import PromptParameters
from vellum.client.types.prompt_request_string_input import PromptRequestStringInput
from vellum.client.types.rich_text_prompt_block import RichTextPromptBlock
from vellum.client.types.string_vellum_value import StringVellumValue
from vellum.client.types.vellum_variable import VellumVariable


def test_execute_prompt_openai__rich_text_system_message(vellum_adhoc_prompt_client):
    """
    Test that execute_prompt sends the correct request structure to OpenAI API
    with a RICH_TEXT block inside a SYSTEM CHAT_MESSAGE.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        expected_outputs: List[PromptOutput] = [StringVellumValue(value="This is a test response from OpenAI.")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    list(
        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream(
            ml_model="gpt-4o-mini",
            input_values=[
                PromptRequestStringInput(key="user_input", type="STRING", value="Hello, world!"),
            ],
            input_variables=[
                VellumVariable(
                    id=str(uuid4()),
                    key="user_input",
                    type="STRING",
                ),
            ],
            parameters=PromptParameters(
                temperature=0.7,
                max_tokens=1024,
            ),
            blocks=[
                ChatMessagePromptBlock(
                    block_type="CHAT_MESSAGE",
                    chat_role="SYSTEM",
                    blocks=[
                        RichTextPromptBlock(
                            block_type="RICH_TEXT",
                            blocks=[],
                        )
                    ],
                ),
            ],
        )
    )

    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 1

    call_kwargs = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0].kwargs

    assert call_kwargs["blocks"] == [
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
                    blocks=[],
                )
            ],
        ),
    ]

    assert call_kwargs["ml_model"] == "gpt-4o-mini"

    assert call_kwargs["parameters"] == PromptParameters(
        stop=None,
        temperature=0.7,
        max_tokens=1024,
        top_p=None,
        top_k=None,
        frequency_penalty=None,
        presence_penalty=None,
        logit_bias=None,
        custom_parameters=None,
    )


def test_execute_prompt_openai__rich_text_with_plain_text(vellum_adhoc_prompt_client):
    """
    Test that execute_prompt sends the correct request structure to OpenAI API
    with a RICH_TEXT block containing PLAIN_TEXT inside a SYSTEM CHAT_MESSAGE.
    """

    def generate_prompt_events(*_args, **_kwargs) -> Iterator[ExecutePromptEvent]:
        execution_id = str(uuid4())
        expected_outputs: List[PromptOutput] = [StringVellumValue(value="This is a test response from OpenAI.")]

        events: List[ExecutePromptEvent] = [
            InitiatedExecutePromptEvent(execution_id=execution_id),
            FulfilledExecutePromptEvent(
                execution_id=execution_id,
                outputs=expected_outputs,
            ),
        ]
        yield from events

    vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.side_effect = generate_prompt_events

    list(
        vellum_adhoc_prompt_client.adhoc_execute_prompt_stream(
            ml_model="gpt-4o",
            input_values=[
                PromptRequestStringInput(key="user_input", type="STRING", value="What is AI?"),
            ],
            input_variables=[
                VellumVariable(
                    id=str(uuid4()),
                    key="user_input",
                    type="STRING",
                ),
            ],
            parameters=PromptParameters(
                temperature=0.0,
                max_tokens=2048,
            ),
            blocks=[
                ChatMessagePromptBlock(
                    block_type="CHAT_MESSAGE",
                    chat_role="SYSTEM",
                    blocks=[
                        RichTextPromptBlock(
                            block_type="RICH_TEXT",
                            blocks=[
                                PlainTextPromptBlock(
                                    block_type="PLAIN_TEXT",
                                    text="You are a helpful AI assistant.",
                                )
                            ],
                        )
                    ],
                ),
            ],
        )
    )

    assert vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_count == 1

    call_kwargs = vellum_adhoc_prompt_client.adhoc_execute_prompt_stream.call_args_list[0].kwargs

    assert call_kwargs["blocks"] == [
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
                            text="You are a helpful AI assistant.",
                        )
                    ],
                )
            ],
        ),
    ]

    assert call_kwargs["ml_model"] == "gpt-4o"
