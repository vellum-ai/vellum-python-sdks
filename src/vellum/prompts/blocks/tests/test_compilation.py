import pytest

from vellum import (
    ChatMessagePromptBlock,
    JinjaPromptBlock,
    PlainTextPromptBlock,
    PromptRequestStringInput,
    RichTextPromptBlock,
    StringVellumValue,
    VariablePromptBlock,
    VellumVariable,
)
from vellum.client.types.json_vellum_value import JsonVellumValue
from vellum.client.types.number_input import NumberInput
from vellum.client.types.prompt_block import PromptBlock
from vellum.client.types.prompt_request_json_input import PromptRequestJsonInput
from vellum.prompts.blocks.compilation import compile_prompt_blocks
from vellum.prompts.blocks.types import CompiledChatMessagePromptBlock, CompiledValuePromptBlock


@pytest.mark.parametrize(
    ["blocks", "inputs", "input_variables", "expected"],
    [
        # Empty
        ([], [], [], []),
        # Jinja
        (
            [JinjaPromptBlock(template="Hello, world!")],
            [],
            [],
            [
                CompiledValuePromptBlock(content=StringVellumValue(value="Hello, world!")),
            ],
        ),
        (
            [JinjaPromptBlock(template="Repeat back to me {{ echo }}")],
            [PromptRequestStringInput(key="echo", value="Hello, world!")],
            [VellumVariable(id="1", type="STRING", key="echo")],
            [
                CompiledValuePromptBlock(content=StringVellumValue(value="Repeat back to me Hello, world!")),
            ],
        ),
        (
            [JinjaPromptBlock(template="{{ re.search('test', message).group() }}")],
            [PromptRequestStringInput(key="message", value="testing")],
            [VellumVariable(id="1", type="STRING", key="message")],
            [
                CompiledValuePromptBlock(content=StringVellumValue(value="test")),
            ],
        ),
        # Rich Text
        (
            [
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text="Hello, world!"),
                    ]
                )
            ],
            [],
            [],
            [
                CompiledValuePromptBlock(content=StringVellumValue(value="Hello, world!")),
            ],
        ),
        (
            [
                RichTextPromptBlock(
                    blocks=[
                        PlainTextPromptBlock(text='Repeat back to me "'),
                        VariablePromptBlock(input_variable="echo"),
                        PlainTextPromptBlock(text='".'),
                    ]
                )
            ],
            [PromptRequestStringInput(key="echo", value="Hello, world!")],
            [VellumVariable(id="901ec2d6-430c-4341-b963-ca689006f5cc", type="STRING", key="echo")],
            [
                CompiledValuePromptBlock(content=StringVellumValue(value='Repeat back to me "Hello, world!".')),
            ],
        ),
        # Chat Message
        (
            [
                ChatMessagePromptBlock(
                    chat_role="USER",
                    blocks=[
                        RichTextPromptBlock(
                            blocks=[
                                PlainTextPromptBlock(text='Repeat back to me "'),
                                VariablePromptBlock(input_variable="echo"),
                                PlainTextPromptBlock(text='".'),
                            ]
                        )
                    ],
                )
            ],
            [PromptRequestStringInput(key="echo", value="Hello, world!")],
            [VellumVariable(id="901ec2d6-430c-4341-b963-ca689006f5cc", type="STRING", key="echo")],
            [
                CompiledChatMessagePromptBlock(
                    role="USER",
                    blocks=[
                        CompiledValuePromptBlock(content=StringVellumValue(value='Repeat back to me "Hello, world!".'))
                    ],
                ),
            ],
        ),
        (
            [
                ChatMessagePromptBlock(
                    chat_role="USER",
                    blocks=[
                        RichTextPromptBlock(
                            blocks=[
                                PlainTextPromptBlock(text="Count to "),
                                VariablePromptBlock(input_variable="count"),
                            ]
                        )
                    ],
                )
            ],
            [
                # TODO: We don't yet have PromptRequestNumberInput. We should either add it or migrate
                # Prompts to using these more generic inputs.
                NumberInput(name="count", value=10),
            ],
            [VellumVariable(id="901ec2d6-430c-4341-b963-ca689006f5cc", type="NUMBER", key="count")],
            [
                CompiledChatMessagePromptBlock(
                    role="USER",
                    blocks=[CompiledValuePromptBlock(content=StringVellumValue(value="Count to 10.0"))],
                ),
            ],
        ),
    ],
    ids=[
        "empty",
        "jinja-no-variables",
        "jinja-with-variables",
        "jinja-with-custom-global",
        "rich-text-no-variables",
        "rich-text-with-variables",
        "chat-message",
        "number-input",
    ],
)
def test_compile_prompt_blocks__happy(blocks, inputs, input_variables, expected):
    actual = compile_prompt_blocks(blocks=blocks, inputs=inputs, input_variables=input_variables)

    assert actual == expected


def test_compile_prompt_blocks__empty_json_variable_with_chat_message_blocks():
    """Test JSON variable handling logic, specifically the empty array skipping behavior."""

    # GIVEN empty array with chat message blocks
    blocks_with_chat: list[PromptBlock] = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="User message")])],
        ),
        VariablePromptBlock(input_variable="json_data"),
    ]

    inputs_with_empty_json = [PromptRequestJsonInput(key="json_data", value=[], type="JSON")]

    input_variables = [VellumVariable(id="901ec2d6-430c-4341-b963-ca689006f5cc", type="JSON", key="json_data")]

    # THEN the empty JSON array should be skipped when there are chat message blocks
    expected_with_chat = [
        CompiledChatMessagePromptBlock(
            role="USER",
            blocks=[CompiledValuePromptBlock(content=StringVellumValue(value="User message"))],
        ),
    ]

    actual = compile_prompt_blocks(
        blocks=blocks_with_chat, inputs=inputs_with_empty_json, input_variables=input_variables
    )
    assert actual == expected_with_chat


def test_compile_prompt_blocks__non_empty_json_variable_with_chat_message_blocks():
    """Test that non-empty JSON variables are included even when there are chat message blocks."""

    # GIVEN non-empty JSON with chat message blocks
    blocks_with_chat: list[PromptBlock] = [
        ChatMessagePromptBlock(
            chat_role="USER",
            blocks=[RichTextPromptBlock(blocks=[PlainTextPromptBlock(text="User message")])],
        ),
        VariablePromptBlock(input_variable="json_data"),
    ]

    inputs_with_non_empty_json = [PromptRequestJsonInput(key="json_data", value={"key": "value"}, type="JSON")]

    input_variables = [VellumVariable(id="901ec2d6-430c-4341-b963-ca689006f5cc", type="JSON", key="json_data")]

    # THEN the non-empty JSON should be included
    expected_with_non_empty = [
        CompiledChatMessagePromptBlock(
            role="USER",
            blocks=[CompiledValuePromptBlock(content=StringVellumValue(value="User message"))],
        ),
        CompiledValuePromptBlock(content=JsonVellumValue(value={"key": "value"})),
    ]

    actual = compile_prompt_blocks(
        blocks=blocks_with_chat, inputs=inputs_with_non_empty_json, input_variables=input_variables
    )
    assert actual == expected_with_non_empty
