import json
import logging
import os
from uuid import uuid4
from typing import Any, Iterable, Iterator, List, Literal, Union, cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionContentPartImageParam,
    ChatCompletionContentPartInputAudioParam,
    ChatCompletionContentPartParam,
    ChatCompletionContentPartRefusalParam,
    ChatCompletionContentPartTextParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_chunk import Choice

from vellum import (
    AdHocExecutePromptEvent,
    FulfilledAdHocExecutePromptEvent,
    InitiatedAdHocExecutePromptEvent,
    RejectedAdHocExecutePromptEvent,
    StreamingAdHocExecutePromptEvent,
    StringVellumValue,
    VellumAudio,
    VellumError,
    VellumImage,
)
from vellum.prompts.blocks.compilation import compile_prompt_blocks
from vellum.prompts.blocks.types import CompiledChatMessagePromptBlock
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes import InlinePromptNode
from vellum.workflows.types.generics import StateType

logger = logging.getLogger(__name__)


class OpenAIChatCompletionNode(InlinePromptNode[StateType]):
    """
    Used to execute a Prompt using the OpenAI API.
    """

    # Override
    def _get_prompt_event_stream(self) -> Iterator[AdHocExecutePromptEvent]:
        client = self._get_client()

        execution_id = str(uuid4())

        yield InitiatedAdHocExecutePromptEvent(
            execution_id=execution_id,
        )

        try:
            stream = client.chat.completions.create(
                messages=self._get_messages(),
                model=self.ml_model,
                # TODO: Add support for additional parameters
                stream=True,
            )
        except Exception as exc:
            yield RejectedAdHocExecutePromptEvent(
                error=VellumError(
                    code=WorkflowErrorCode.PROVIDER_ERROR,
                    message=exc.args[0],
                ),
                execution_id=execution_id,
            )
            return

        combined_delta_content = ""
        for chunk in stream:
            choices: List[Choice] = chunk.choices
            if len(choices) != 1:
                yield RejectedAdHocExecutePromptEvent(
                    error=VellumError(
                        code=WorkflowErrorCode.PROVIDER_ERROR,
                        message="Expected one choice per chunk, but found more than one.",
                    ),
                    execution_id=execution_id,
                )
                return

            choice = choices[0]
            delta = choice.delta

            if delta.tool_calls:
                # TODO: Add support for tool calls
                raise NotImplementedError("This node hasn't been extended to support tool calling yet.")

            if delta.content:
                combined_delta_content += delta.content

            StreamingAdHocExecutePromptEvent(
                output=StringVellumValue(value=delta.content),
                # TODO: Add support for multiple outputs
                output_index=1,
                execution_id=execution_id,
            )

        yield FulfilledAdHocExecutePromptEvent(
            # TODO: Add support for multiple outputs
            outputs=[
                StringVellumValue(value=combined_delta_content),
            ],
            execution_id=execution_id,
        )

    def _get_client(self) -> OpenAI:
        """Used to retrieve an API client for interacting with the OpenAI API.

        Note: This method can be overridden if you'd like to use your own API client that conforms to the same
            interfaces as that of OpenAI.
        """

        openai_api_key = os.environ.get("OPENAI_API_KEY")

        if not openai_api_key:
            raise NodeException(
                code=WorkflowErrorCode.INTERNAL_ERROR,
                message="Unable to determine an OpenAI API key.",
            )

        client = OpenAI(api_key=openai_api_key)
        return client

    def _get_messages(self) -> Iterable[ChatCompletionMessageParam]:
        input_variables, input_values = self._compile_prompt_inputs()

        compiled_blocks = compile_prompt_blocks(
            blocks=self.blocks, inputs=input_values, input_variables=input_variables
        )

        chat_message_blocks: list[CompiledChatMessagePromptBlock] = [
            block for block in compiled_blocks if block.block_type == "CHAT_MESSAGE"
        ]
        messages = [self._create_message(block) for block in chat_message_blocks]

        return messages

    @classmethod
    def _create_message(cls, chat_message_block: CompiledChatMessagePromptBlock) -> ChatCompletionMessageParam:
        name = chat_message_block.source
        content = cls._create_message_content(chat_message_block)

        if chat_message_block.role == "SYSTEM":
            relevant_system_content = [
                cast(ChatCompletionContentPartTextParam, c) for c in content if c["type"] == "text"
            ]
            system_message: ChatCompletionSystemMessageParam = {
                "content": relevant_system_content,
                "role": "system",
            }
            if name:
                system_message["name"] = name

            return system_message
        elif chat_message_block.role == "USER":
            user_message: ChatCompletionUserMessageParam = {
                "content": content,
                "role": "user",
            }
            if name:
                user_message["name"] = name

            return user_message
        elif chat_message_block.role == "ASSISTANT":
            relevant_assistant_content = [
                cast(Union[ChatCompletionContentPartTextParam, ChatCompletionContentPartRefusalParam], c)
                for c in content
                if c["type"] in ["text", "refusal"]
            ]
            assistant_message: ChatCompletionAssistantMessageParam = {
                "content": relevant_assistant_content,
                "role": "assistant",
            }
            if name:
                assistant_message["name"] = name

            return assistant_message
        else:
            logger.error(f"Unexpected role: {chat_message_block.role}")
            raise NodeException(
                code=WorkflowErrorCode.INTERNAL_ERROR, message="Unexpected role found when compiling prompt blocks"
            )

    @classmethod
    def _create_message_content(
        cls,
        chat_message_block: CompiledChatMessagePromptBlock,
    ) -> List[ChatCompletionContentPartParam]:
        content: List[ChatCompletionContentPartParam] = []
        for block in chat_message_block.blocks:
            if block.content.type == "STRING":
                string_value = cast(str, block.content.value)
                string_content_item: ChatCompletionContentPartTextParam = {"type": "text", "text": string_value}
                content.append(string_content_item)
            elif block.content.type == "JSON":
                json_value = cast(Any, block.content.value)
                json_content_item: ChatCompletionContentPartTextParam = {"type": "text", "text": json.dumps(json_value)}
                content.append(json_content_item)
            elif block.content.type == "IMAGE":
                image_value = cast(VellumImage, block.content.value)
                image_content_item: ChatCompletionContentPartImageParam = {
                    "type": "image_url",
                    "image_url": {"url": image_value.src},
                }
                if image_value.metadata and image_value.metadata.get("detail"):
                    detail = image_value.metadata["detail"]

                    if detail not in ["auto", "low", "high"]:
                        raise NodeException(
                            code=WorkflowErrorCode.INTERNAL_ERROR,
                            message="Image detail must be one of 'auto', 'low', or 'high.",
                        )

                    image_content_item["image_url"]["detail"] = cast(Literal["auto", "low", "high"], detail)

                content.append(image_content_item)
            elif block.content.type == "AUDIO":
                audio_value = cast(VellumAudio, block.content.value)
                audio_value_src_parts = audio_value.src.split(",")
                if len(audio_value_src_parts) != 2:
                    raise NodeException(
                        code=WorkflowErrorCode.INTERNAL_ERROR, message="Audio data is not properly encoded."
                    )
                _, cleaned_audio_value = audio_value_src_parts
                if not audio_value.metadata:
                    raise NodeException(
                        code=WorkflowErrorCode.INTERNAL_ERROR, message="Audio metadata is required for audio input."
                    )
                audio_format = audio_value.metadata.get("format")
                if not audio_format:
                    raise NodeException(
                        code=WorkflowErrorCode.INTERNAL_ERROR, message="Audio format is required for audio input."
                    )
                if audio_format not in {"wav", "mp3"}:
                    raise NodeException(
                        code=WorkflowErrorCode.INTERNAL_ERROR,
                        message="Audio format must be one of 'wav' or 'mp3'.",
                    )

                audio_content_item: ChatCompletionContentPartInputAudioParam = {
                    "type": "input_audio",
                    "input_audio": {
                        "data": cleaned_audio_value,
                        "format": cast(Literal["wav", "mp3"], audio_format),
                    },
                }

                content.append(audio_content_item)
            elif block.content.type == "DOCUMENT":
                raise NodeException(
                    code=WorkflowErrorCode.PROVIDER_ERROR,
                    message="Document chat message content type is not currently supported",
                )
            else:
                raise NodeException(
                    code=WorkflowErrorCode.INTERNAL_ERROR,
                    message=f"Failed to parse chat message block {block.content.type}",
                )

        return content
