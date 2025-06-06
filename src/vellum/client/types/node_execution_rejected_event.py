# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .api_request_parent_context import ApiRequestParentContext
from .node_parent_context import NodeParentContext
from .prompt_deployment_parent_context import PromptDeploymentParentContext
from .span_link import SpanLink
from .workflow_deployment_parent_context import WorkflowDeploymentParentContext
from .workflow_parent_context import WorkflowParentContext
from .workflow_sandbox_parent_context import WorkflowSandboxParentContext
import typing
from .parent_context import ParentContext
from .node_execution_rejected_body import NodeExecutionRejectedBody
import datetime as dt
from .api_version_enum import ApiVersionEnum
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class NodeExecutionRejectedEvent(UniversalBaseModel):
    parent: typing.Optional[ParentContext] = None
    links: typing.Optional[typing.List[SpanLink]] = None
    name: typing.Literal["node.execution.rejected"] = "node.execution.rejected"
    body: NodeExecutionRejectedBody
    id: str
    timestamp: dt.datetime
    api_version: typing.Optional[ApiVersionEnum] = None
    trace_id: str
    span_id: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
