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
    ],
    ids=[
        "empty",
        "jinja-no-variables",
        "jinja-with-variables",
        "rich-text-no-variables",
        "rich-text-with-variables",
        "chat-message",
    ],
)
def test_compile_prompt_blocks__happy(blocks, inputs, input_variables, expected):
    actual = compile_prompt_blocks(blocks=blocks, inputs=inputs, input_variables=input_variables)

    assert actual == expected
