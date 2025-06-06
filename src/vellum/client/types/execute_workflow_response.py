# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .execute_workflow_workflow_result_event import ExecuteWorkflowWorkflowResultEvent
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class ExecuteWorkflowResponse(UniversalBaseModel):
    execution_id: str
    run_id: typing.Optional[str] = None
    external_id: typing.Optional[str] = None
    data: ExecuteWorkflowWorkflowResultEvent

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
