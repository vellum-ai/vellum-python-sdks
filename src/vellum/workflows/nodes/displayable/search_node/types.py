from typing import Any, List, Optional, Union

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.condition_combinator import ConditionCombinator
from vellum.client.types.logical_operator import LogicalOperator


class MetadataLogicalConditionGroup(UniversalBaseModel):
    combinator: ConditionCombinator
    negated: bool
    conditions: List["MetadataLogicalExpression"]


class MetadataLogicalCondition(UniversalBaseModel):
    lhs_variable: Any
    operator: LogicalOperator
    rhs_variable: Any


MetadataLogicalExpression = Union[MetadataLogicalConditionGroup, MetadataLogicalCondition]


class SearchFilters(UniversalBaseModel):
    external_ids: Optional[List[str]] = None
    metadata: Optional[MetadataLogicalConditionGroup] = None
