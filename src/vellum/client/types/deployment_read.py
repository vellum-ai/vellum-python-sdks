# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import datetime as dt
import pydantic
import typing
from .entity_status import EntityStatus
from .environment_enum import EnvironmentEnum
from .vellum_variable import VellumVariable
from ..core.pydantic_utilities import IS_PYDANTIC_V2
from ..core.pydantic_utilities import update_forward_refs


class DeploymentRead(UniversalBaseModel):
    id: str
    created: dt.datetime
    label: str = pydantic.Field()
    """
    A human-readable label for the deployment
    """

    name: str = pydantic.Field()
    """
    A name that uniquely identifies this deployment within its workspace
    """

    status: typing.Optional[EntityStatus] = pydantic.Field(default=None)
    """
    The current status of the deployment
    
    - `ACTIVE` - Active
    - `ARCHIVED` - Archived
    """

    environment: typing.Optional[EnvironmentEnum] = pydantic.Field(default=None)
    """
    The environment this deployment is used in
    
    - `DEVELOPMENT` - Development
    - `STAGING` - Staging
    - `PRODUCTION` - Production
    """

    last_deployed_on: dt.datetime
    input_variables: typing.List[VellumVariable]
    description: typing.Optional[str] = pydantic.Field(default=None)
    """
    A human-readable description of the deployment
    """

    active_model_version_ids: typing.List[str] = pydantic.Field()
    """
    Deprecated. The Prompt execution endpoints return a `prompt_version_id` that could be used instead.
    """

    last_deployed_history_item_id: str = pydantic.Field()
    """
    The ID of the history item associated with this Deployment's LATEST Release Tag
    """

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(ArrayVellumValue, DeploymentRead=DeploymentRead)
