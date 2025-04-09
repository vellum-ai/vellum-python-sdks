# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .vellum_value import VellumValue
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class CodeExecutionNodeArrayResult(UniversalBaseModel):
    id: str
    type: typing.Literal["ARRAY"] = "ARRAY"
    value: typing.Optional[typing.List[VellumValue]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
