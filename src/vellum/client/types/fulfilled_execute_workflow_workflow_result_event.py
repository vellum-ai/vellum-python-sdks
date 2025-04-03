# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
import datetime as dt
from .workflow_output import WorkflowOutput
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class FulfilledExecuteWorkflowWorkflowResultEvent(UniversalBaseModel):
    """
    The successful response from the Workflow execution containing the produced outputs.
    """

    id: str
    state: typing.Literal["FULFILLED"] = "FULFILLED"
    ts: dt.datetime
    outputs: typing.List[WorkflowOutput]

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(
    ArrayVellumValue, FulfilledExecuteWorkflowWorkflowResultEvent=FulfilledExecuteWorkflowWorkflowResultEvent
)
