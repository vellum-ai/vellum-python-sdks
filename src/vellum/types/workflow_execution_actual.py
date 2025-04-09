# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
from .execution_vellum_value import ExecutionVellumValue
import datetime as dt
import typing
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class WorkflowExecutionActual(UniversalBaseModel):
    output: ExecutionVellumValue
    timestamp: dt.datetime
    quality: float
    metadata: typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
