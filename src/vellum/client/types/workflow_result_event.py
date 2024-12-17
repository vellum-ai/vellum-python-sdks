# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .array_variable_value import ArrayVariableValue
from .array_vellum_value import ArrayVellumValue
from .workflow_node_result_event_state import WorkflowNodeResultEventState
import datetime as dt
import typing
from .workflow_result_event_output_data import WorkflowResultEventOutputData
from .workflow_event_error import WorkflowEventError
from .workflow_output import WorkflowOutput
from .execution_vellum_value import ExecutionVellumValue
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class WorkflowResultEvent(UniversalBaseModel):
    id: str
    state: WorkflowNodeResultEventState
    ts: dt.datetime
    output: typing.Optional[WorkflowResultEventOutputData] = None
    error: typing.Optional[WorkflowEventError] = None
    outputs: typing.Optional[typing.List[WorkflowOutput]] = None
    inputs: typing.Optional[typing.List[ExecutionVellumValue]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVariableValue, WorkflowResultEvent=WorkflowResultEvent)
update_forward_refs(ArrayVellumValue, WorkflowResultEvent=WorkflowResultEvent)