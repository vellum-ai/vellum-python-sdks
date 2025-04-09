# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
from .workflow_result_event import WorkflowResultEvent
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class WorkflowExecutionWorkflowResultEvent(UniversalBaseModel):
    """
    A WORKFLOW-level event emitted from the workflow's execution.
    """

    execution_id: str
    run_id: typing.Optional[str] = None
    external_id: typing.Optional[str] = None
    type: typing.Literal["WORKFLOW"] = "WORKFLOW"
    data: WorkflowResultEvent

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
