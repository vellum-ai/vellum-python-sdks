# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .chat_message import ChatMessage
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class TestSuiteRunExecutionChatHistoryOutput(UniversalBaseModel):
    """
    Execution output of an entity evaluated during a Test Suite Run that is of type CHAT_HISTORY
    """

    name: str
    type: typing.Literal["CHAT_HISTORY"] = "CHAT_HISTORY"
    value: typing.Optional[typing.List[ChatMessage]] = None
    output_variable_id: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
