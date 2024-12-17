# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .iteration_state_enum import IterationStateEnum
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class MapNodeResultData(UniversalBaseModel):
    execution_ids: typing.List[str]
    iteration_state: typing.Optional[IterationStateEnum] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow