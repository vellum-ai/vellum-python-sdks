# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .rich_text_child_block_request import RichTextChildBlockRequest
from .prompt_block_state import PromptBlockState
from .ephemeral_prompt_cache_config_request import EphemeralPromptCacheConfigRequest
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class RichTextPromptBlockRequest(UniversalBaseModel):
    """
    A block that includes a combination of plain text and variable blocks.
    """

    block_type: typing.Literal["RICH_TEXT"] = "RICH_TEXT"
    blocks: typing.List[RichTextChildBlockRequest]
    id: str
    state: typing.Optional[PromptBlockState] = None
    cache_config: typing.Optional[EphemeralPromptCacheConfigRequest] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow