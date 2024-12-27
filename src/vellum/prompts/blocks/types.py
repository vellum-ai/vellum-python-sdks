from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from vellum import ArrayVellumValue, ChatMessageRole, EphemeralPromptCacheConfig, VellumValue
from vellum.client.core import UniversalBaseModel


class BaseCompiledPromptBlock(UniversalBaseModel):
    cache_config: Optional[EphemeralPromptCacheConfig] = None


class CompiledValuePromptBlock(BaseCompiledPromptBlock):
    block_type: Literal["VALUE"] = "VALUE"
    content: VellumValue


class CompiledChatMessagePromptBlock(BaseCompiledPromptBlock):
    block_type: Literal["CHAT_MESSAGE"] = "CHAT_MESSAGE"
    role: ChatMessageRole = "ASSISTANT"
    unterminated: bool = False
    blocks: list[CompiledValuePromptBlock] = []
    source: Optional[str] = None


CompiledPromptBlock = Annotated[
    Union[
        CompiledValuePromptBlock,
        CompiledChatMessagePromptBlock,
    ],
    "block_type",
]

ArrayVellumValue.model_rebuild()

CompiledValuePromptBlock.model_rebuild()
