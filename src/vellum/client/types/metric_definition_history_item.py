# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
from .array_vellum_value import ArrayVellumValue
import pydantic
import typing
from .vellum_variable import VellumVariable
from ..core.pydantic_utilities import IS_PYDANTIC_V2


class MetricDefinitionHistoryItem(UniversalBaseModel):
    id: str
    label: str = pydantic.Field()
    """
    A human-readable label for the metric
    """

    name: str = pydantic.Field()
    """
    A name that uniquely identifies this metric within its workspace
    """

    description: str
    input_variables: typing.List[VellumVariable]
    output_variables: typing.List[VellumVariable]

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
