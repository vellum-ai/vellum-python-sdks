from typing import Any, List, Optional, Union

from vellum.client.core.pydantic_utilities import UniversalBaseModel
from vellum.client.types.condition_combinator import ConditionCombinator
from vellum.client.types.logical_operator import LogicalOperator
from vellum.client.types.vellum_value_logical_condition_group_request import VellumValueLogicalConditionGroupRequest
from vellum.client.types.vellum_value_logical_condition_request import VellumValueLogicalConditionRequest
from vellum.workflows.nodes.displayable.bases.utils import primitive_to_vellum_value_request


class MetadataLogicalConditionGroup(UniversalBaseModel):
    combinator: ConditionCombinator
    negated: bool
    conditions: List["MetadataLogicalExpression"]

    def to_request(self) -> VellumValueLogicalConditionGroupRequest:
        return VellumValueLogicalConditionGroupRequest(
            combinator=self.combinator,
            negated=self.negated,
            conditions=[c.to_request() for c in self.conditions],
        )


class MetadataLogicalCondition(UniversalBaseModel):
    lhs_variable: Any
    operator: LogicalOperator
    rhs_variable: Any = None

    def to_request(self) -> VellumValueLogicalConditionRequest:
        return VellumValueLogicalConditionRequest(
            lhs_variable=primitive_to_vellum_value_request(self.lhs_variable),
            operator=self.operator,
            rhs_variable=primitive_to_vellum_value_request(self.rhs_variable),
        )


MetadataLogicalExpression = Union[MetadataLogicalConditionGroup, MetadataLogicalCondition]


class SearchFilters(UniversalBaseModel):
    external_ids: Optional[List[str]] = None
    metadata: Optional[MetadataLogicalConditionGroup] = None
