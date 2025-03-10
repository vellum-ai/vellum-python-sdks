# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import pydantic
from .release_tag_source import ReleaseTagSource
from .workflow_release_tag_workflow_deployment_history_item import WorkflowReleaseTagWorkflowDeploymentHistoryItem
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import typing


class WorkflowReleaseTagRead(UniversalBaseModel):
    name: str = pydantic.Field()
    """
    The name of the Release Tag
    """

    source: ReleaseTagSource = pydantic.Field()
    """
    The source of how the Release Tag was originally created
    
    * `SYSTEM` - System
    * `USER` - User
    """

    history_item: WorkflowReleaseTagWorkflowDeploymentHistoryItem = pydantic.Field()
    """
    The Workflow Deployment History Item that this Release Tag is associated with
    """

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
