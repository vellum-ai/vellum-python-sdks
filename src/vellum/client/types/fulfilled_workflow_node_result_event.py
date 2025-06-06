# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import typing
import datetime as dt
from .workflow_node_result_data import WorkflowNodeResultData
from .node_output_compiled_value import NodeOutputCompiledValue
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class FulfilledWorkflowNodeResultEvent(UniversalBaseModel):
    """
    An event that indicates that the node has fulfilled its execution.
    """

    id: str
    node_id: str
    node_result_id: str
    state: typing.Literal["FULFILLED"] = "FULFILLED"
    ts: typing.Optional[dt.datetime] = None
    data: typing.Optional[WorkflowNodeResultData] = None
    source_execution_id: typing.Optional[str] = None
    output_values: typing.List[NodeOutputCompiledValue]
    mocked: typing.Optional[bool] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
