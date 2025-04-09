# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import pydantic
import typing
from .entity_status import EntityStatus
from .environment_enum import EnvironmentEnum
import datetime as dt
from .vellum_variable import VellumVariable
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class SlimWorkflowDeployment(UniversalBaseModel):
    id: str
    name: str = pydantic.Field()
    """
    A name that uniquely identifies this workflow deployment within its workspace
    """

    label: str = pydantic.Field()
    """
    A human-readable label for the workflow deployment
    """

    status: typing.Optional[EntityStatus] = pydantic.Field(default=None)
    """
    The current status of the workflow deployment
    
    * `ACTIVE` - Active
    * `ARCHIVED` - Archived
    """

    environment: typing.Optional[EnvironmentEnum] = pydantic.Field(default=None)
    """
    The environment this workflow deployment is used in
    
    * `DEVELOPMENT` - Development
    * `STAGING` - Staging
    * `PRODUCTION` - Production
    """

    created: dt.datetime
    last_deployed_on: dt.datetime
    input_variables: typing.List[VellumVariable] = pydantic.Field()
    """
    The input variables this Workflow Deployment expects to receive values for when it is executed.
    """

    output_variables: typing.List[VellumVariable] = pydantic.Field()
    """
    The output variables this Workflow Deployment will produce when it is executed.
    """

    description: typing.Optional[str] = pydantic.Field(default=None)
    """
    A human-readable description of the workflow deployment
    """

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
