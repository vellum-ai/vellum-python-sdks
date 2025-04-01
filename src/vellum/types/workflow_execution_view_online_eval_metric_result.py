# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .execution_vellum_value import ExecutionVellumValue
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class WorkflowExecutionViewOnlineEvalMetricResult(UniversalBaseModel):
    outputs: typing.List[ExecutionVellumValue]
    label: str
    metric_id: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(
    ArrayVellumValue, WorkflowExecutionViewOnlineEvalMetricResult=WorkflowExecutionViewOnlineEvalMetricResult
)
