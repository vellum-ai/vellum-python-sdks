import json
from typing import Sequence, Union, cast

from vellum import (
    ChatMessage,
    DocumentVellumValue,
    JsonVellumValue,
    PromptBlock,
    PromptRequestInput,
    RichTextPromptBlock,
    StringVellumValue,
    VellumDocument,
    VellumVariable,
)
from vellum.client.types.audio_vellum_value import AudioVellumValue
from vellum.client.types.function_call import FunctionCall
from vellum.client.types.function_call_vellum_value import FunctionCallVellumValue
from vellum.client.types.image_vellum_value import ImageVellumValue
from vellum.client.types.number_input import NumberInput
from vellum.client.types.vellum_audio import VellumAudio
from vellum.client.types.vellum_image import VellumImage
from vellum.prompts.blocks.exceptions import PromptCompilationError
from vellum.prompts.blocks.types import CompiledChatMessagePromptBlock, CompiledPromptBlock, CompiledValuePromptBlock
from vellum.utils.templating.constants import DEFAULT_JINJA_CUSTOM_FILTERS, DEFAULT_JINJA_GLOBALS
from vellum.utils.templating.render import render_sandboxed_jinja_template
from vellum.utils.typing import cast_not_optional

PromptInput = Union[PromptRequestInput, NumberInput]


def compile_prompt_blocks(
    blocks: list[PromptBlock],
    inputs: Sequence[PromptInput],
    input_variables: list[VellumVariable],
) -> list[CompiledPromptBlock]:
    """Compiles a list of Prompt Blocks, performing all variable substitutions and Jinja templating needed."""

    sanitized_inputs = _sanitize_inputs(inputs)
    inputs_by_name = {
        (input_.name if isinstance(input_, NumberInput) else input_.key): input_ for input_ in sanitized_inputs
    }

    compiled_blocks: list[CompiledPromptBlock] = []
    for block in blocks:
        if block.state == "DISABLED":
            continue

        if block.block_type == "CHAT_MESSAGE":
            chat_role = cast_not_optional(block.chat_role)
            inner_blocks = cast_not_optional(block.blocks)
            unterminated = block.chat_message_unterminated or False

            inner_prompt_blocks = compile_prompt_blocks(
                inner_blocks,
                sanitized_inputs,
                input_variables,
            )
            if not inner_prompt_blocks:
                continue

            compiled_blocks.append(
                CompiledChatMessagePromptBlock(
                    role=chat_role,
                    unterminated=unterminated,
                    source=block.chat_source,
                    blocks=[inner for inner in inner_prompt_blocks if inner.block_type == "VALUE"],
                    cache_config=block.cache_config,
                )
            )

        elif block.block_type == "JINJA":
            if block.template is None:
                continue

            rendered_template = render_sandboxed_jinja_template(
                template=block.template,
                input_values={name: inp.value for name, inp in inputs_by_name.items()},
                jinja_custom_filters=DEFAULT_JINJA_CUSTOM_FILTERS,
                jinja_globals=DEFAULT_JINJA_GLOBALS,
            )
            jinja_content = StringVellumValue(value=rendered_template)

            compiled_blocks.append(
                CompiledValuePromptBlock(
                    content=jinja_content,
                    cache_config=block.cache_config,
                )
            )

        elif block.block_type == "VARIABLE":
            compiled_input = inputs_by_name.get(block.input_variable)
            if compiled_input is None:
                raise PromptCompilationError(f"Input variable '{block.input_variable}' not found")

            if compiled_input.type == "CHAT_HISTORY":
                history = cast(list[ChatMessage], compiled_input.value)
                chat_message_blocks = _compile_chat_messages_as_prompt_blocks(history)
                compiled_blocks.extend(chat_message_blocks)
                continue

            if compiled_input.type == "STRING":
                compiled_blocks.append(
                    CompiledValuePromptBlock(
                        content=StringVellumValue(value=compiled_input.value),
                        cache_config=block.cache_config,
                    )
                )
            elif compiled_input == "JSON":
                compiled_blocks.append(
                    CompiledValuePromptBlock(
                        content=JsonVellumValue(value=compiled_input.value),
                        cache_config=block.cache_config,
                    )
                )
            elif compiled_input.type == "CHAT_HISTORY":
                chat_message_blocks = _compile_chat_messages_as_prompt_blocks(compiled_input.value)
                compiled_blocks.extend(chat_message_blocks)
            else:
                raise PromptCompilationError(f"Invalid input type for variable block: {compiled_input.type}")

        elif block.block_type == "RICH_TEXT":
            value_block = _compile_rich_text_block_as_value_block(block=block, inputs=sanitized_inputs)
            compiled_blocks.append(value_block)

        elif block.block_type == "FUNCTION_DEFINITION":
            raise PromptCompilationError("Function definitions shouldn't go through compilation process")

        elif block.block_type == "FUNCTION_CALL":
            function_call_block = CompiledValuePromptBlock(
                content=FunctionCallVellumValue(
                    value=FunctionCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.arguments,
                    ),
                ),
                cache_config=block.cache_config,
            )
            compiled_blocks.append(function_call_block)

        elif block.block_type == "IMAGE":
            image_block = CompiledValuePromptBlock(
                content=ImageVellumValue(
                    value=VellumImage(
                        src=block.src,
                        metadata=block.metadata,
                    ),
                ),
                cache_config=block.cache_config,
            )
            compiled_blocks.append(image_block)

        elif block.block_type == "AUDIO":
            audio_block = CompiledValuePromptBlock(
                content=AudioVellumValue(
                    value=VellumAudio(
                        src=block.src,
                        metadata=block.metadata,
                    ),
                ),
                cache_config=block.cache_config,
            )
            compiled_blocks.append(audio_block)

        elif block.block_type == "DOCUMENT":
            document_block = CompiledValuePromptBlock(
                content=DocumentVellumValue(
                    value=VellumDocument(
                        src=block.src,
                        metadata=block.metadata,
                    )
                ),
                cache_config=block.cache_config,
            )
            compiled_blocks.append(document_block)
        else:
            raise PromptCompilationError(f"Unknown block_type: {block.block_type}")

    return compiled_blocks


def _compile_chat_messages_as_prompt_blocks(chat_messages: list[ChatMessage]) -> list[CompiledChatMessagePromptBlock]:
    blocks: list[CompiledChatMessagePromptBlock] = []
    for chat_message in chat_messages:
        if chat_message.content is None:
            continue

        chat_message_blocks = (
            [
                CompiledValuePromptBlock(
                    content=item,
                )
                for item in chat_message.content.value
            ]
            if chat_message.content.type == "ARRAY"
            else [
                CompiledValuePromptBlock(
                    content=chat_message.content,
                )
            ]
        )

        blocks.append(
            CompiledChatMessagePromptBlock(
                role=chat_message.role,
                unterminated=False,
                blocks=chat_message_blocks,
                source=chat_message.source,
            )
        )

    return blocks


def _compile_rich_text_block_as_value_block(
    block: RichTextPromptBlock,
    inputs: list[PromptInput],
) -> CompiledValuePromptBlock:
    value: str = ""
    inputs_by_name = {(input_.name if isinstance(input_, NumberInput) else input_.key): input_ for input_ in inputs}
    for child_block in block.blocks:
        if child_block.block_type == "PLAIN_TEXT":
            value += child_block.text
        elif child_block.block_type == "VARIABLE":
            input = inputs_by_name.get(child_block.input_variable)
            if input is None:
                raise PromptCompilationError(f"Input variable '{child_block.input_variable}' not found")
            elif input.type == "STRING":
                value += str(input.value)
            elif input.type == "JSON":
                value += json.dumps(input.value, indent=4)
            elif input.type == "NUMBER":
                value += str(input.value)
            else:
                raise PromptCompilationError(
                    f"Input variable '{child_block.input_variable}' has an invalid type: {input.type}"
                )
        else:
            raise PromptCompilationError(f"Invalid child block_type for RICH_TEXT: {child_block.block_type}")

    return CompiledValuePromptBlock(content=StringVellumValue(value=value), cache_config=block.cache_config)


def _sanitize_inputs(inputs: Sequence[PromptInput]) -> list[PromptInput]:
    sanitized_inputs: list[PromptInput] = []
    for input_ in inputs:
        if input_.type == "CHAT_HISTORY" and input_.value is None:
            sanitized_inputs.append(input_.model_copy(update={"value": cast(list[ChatMessage], [])}))
        elif input_.type == "STRING" and input_.value is None:
            sanitized_inputs.append(input_.model_copy(update={"value": ""}))
        else:
            sanitized_inputs.append(input_)

    return sanitized_inputs
