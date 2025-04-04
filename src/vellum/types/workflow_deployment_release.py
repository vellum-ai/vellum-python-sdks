# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import datetime as dt
from .release_environment import ReleaseEnvironment
import typing
from .release_created_by import ReleaseCreatedBy
from .workflow_deployment_release_workflow_version import WorkflowDeploymentReleaseWorkflowVersion
from .release_release_tag import ReleaseReleaseTag
from .slim_release_review import SlimReleaseReview
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class WorkflowDeploymentRelease(UniversalBaseModel):
    id: str
    created: dt.datetime
    environment: ReleaseEnvironment
    created_by: typing.Optional[ReleaseCreatedBy] = None
    workflow_version: WorkflowDeploymentReleaseWorkflowVersion
    description: typing.Optional[str] = None
    release_tags: typing.List[ReleaseReleaseTag]
    reviews: typing.List[SlimReleaseReview]

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
