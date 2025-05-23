# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .vellum_code_resource_definition import VellumCodeResourceDefinition
from .base_output import BaseOutput
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import typing
import pydantic


class WorkflowExecutionStreamingBody(UniversalBaseModel):
    workflow_definition: VellumCodeResourceDefinition
    output: BaseOutput

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
