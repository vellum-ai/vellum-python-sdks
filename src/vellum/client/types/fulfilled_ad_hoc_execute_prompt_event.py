# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .prompt_output import PromptOutput
from .ad_hoc_fulfilled_prompt_execution_meta import AdHocFulfilledPromptExecutionMeta
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class FulfilledAdHocExecutePromptEvent(UniversalBaseModel):
    """
    The final data event returned indicating that the stream has ended and all final resolved values from the model can be found.
    """

    state: typing.Literal["FULFILLED"] = "FULFILLED"
    outputs: typing.List[PromptOutput]
    execution_id: str
    meta: typing.Optional[AdHocFulfilledPromptExecutionMeta] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
