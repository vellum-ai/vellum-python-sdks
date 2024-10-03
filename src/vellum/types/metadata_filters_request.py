# This file was auto-generated by Fern from our API Definition.

from __future__ import annotations
from ..core.pydantic_utilities import UniversalBaseModel
from .logical_condition_group_request import LogicalConditionGroupRequest
from .array_vellum_value_request import ArrayVellumValueRequest
from .logical_expression_request import LogicalExpressionRequest
import typing
from .metadata_resolver_variable_request import MetadataResolverVariableRequest
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic
from ..core.pydantic_utilities import update_forward_refs


class MetadataFiltersRequest(UniversalBaseModel):
    """
    A filter that follows Vellum's ResolvableLogicalExpression pattern.
    """

    expression: LogicalExpressionRequest
    variables: typing.List[MetadataResolverVariableRequest]

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow


update_forward_refs(LogicalConditionGroupRequest, MetadataFiltersRequest=MetadataFiltersRequest)
update_forward_refs(ArrayVellumValueRequest, MetadataFiltersRequest=MetadataFiltersRequest)
