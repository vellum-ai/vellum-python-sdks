# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .api_request_parent_context import ApiRequestParentContext
from .node_parent_context import NodeParentContext
from .prompt_deployment_parent_context import PromptDeploymentParentContext
from .span_link import SpanLink
from .workflow_deployment_parent_context import WorkflowDeploymentParentContext
from .workflow_parent_context import WorkflowParentContext
from .workflow_sandbox_parent_context import WorkflowSandboxParentContext
from .array_vellum_value import ArrayVellumValue
import typing
import datetime as dt
from .execution_vellum_value import ExecutionVellumValue
from .workflow_error import WorkflowError
from .workflow_execution_actual import WorkflowExecutionActual
from .workflow_execution_view_online_eval_metric_result import WorkflowExecutionViewOnlineEvalMetricResult
from .workflow_execution_usage_result import WorkflowExecutionUsageResult
from .vellum_span import VellumSpan
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class WorkflowEventExecutionRead(UniversalBaseModel):
    span_id: str
    parent_context: typing.Optional[WorkflowDeploymentParentContext] = None
    start: dt.datetime
    end: typing.Optional[dt.datetime] = None
    inputs: typing.List[ExecutionVellumValue]
    outputs: typing.List[ExecutionVellumValue]
    error: typing.Optional[WorkflowError] = None
    latest_actual: typing.Optional[WorkflowExecutionActual] = None
    metric_results: typing.List[WorkflowExecutionViewOnlineEvalMetricResult]
    usage_results: typing.Optional[typing.List[WorkflowExecutionUsageResult]] = None
    spans: typing.List[VellumSpan]
    state: typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]] = None

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
