# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
import typing
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class PromptDeploymentParentContext(UniversalBaseModel):
    parent: typing.Optional["ParentContext"] = None
    links: typing.Optional[typing.List["SpanLink"]] = None
    type: typing.Literal["PROMPT_RELEASE_TAG"] = "PROMPT_RELEASE_TAG"
    span_id: str
    deployment_id: str
    deployment_name: str
    deployment_history_item_id: str
    release_tag_id: str
    release_tag_name: str
    external_id: typing.Optional[str] = None
    metadata: typing.Optional[typing.Dict[str, typing.Optional[typing.Any]]] = None
    prompt_version_id: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


from .api_request_parent_context import ApiRequestParentContext  # noqa: E402
from .node_parent_context import NodeParentContext  # noqa: E402
from .span_link import SpanLink  # noqa: E402
from .workflow_deployment_parent_context import WorkflowDeploymentParentContext  # noqa: E402
from .workflow_parent_context import WorkflowParentContext  # noqa: E402
from .workflow_sandbox_parent_context import WorkflowSandboxParentContext  # noqa: E402
from .parent_context import ParentContext  # noqa: E402

update_forward_refs(ApiRequestParentContext, PromptDeploymentParentContext=PromptDeploymentParentContext)
update_forward_refs(NodeParentContext, PromptDeploymentParentContext=PromptDeploymentParentContext)
update_forward_refs(SpanLink, PromptDeploymentParentContext=PromptDeploymentParentContext)
update_forward_refs(WorkflowDeploymentParentContext, PromptDeploymentParentContext=PromptDeploymentParentContext)
update_forward_refs(WorkflowParentContext, PromptDeploymentParentContext=PromptDeploymentParentContext)
update_forward_refs(WorkflowSandboxParentContext, PromptDeploymentParentContext=PromptDeploymentParentContext)
update_forward_refs(PromptDeploymentParentContext)
