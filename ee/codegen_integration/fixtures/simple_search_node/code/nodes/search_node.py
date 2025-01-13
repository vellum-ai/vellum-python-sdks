from vellum import SearchResultMergingRequest, SearchWeightsRequest
from vellum.workflows.nodes.displayable import SearchNode as BaseSearchNode
from vellum.workflows.nodes.displayable.bases.types import (
    MetadataLogicalCondition,
    MetadataLogicalConditionGroup,
    SearchFilters,
)

from ..inputs import Inputs


class SearchNode(BaseSearchNode):
    query = Inputs.query
    document_index = "my-sweet-document"
    limit = 8
    weights = SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2)
    result_merging = SearchResultMergingRequest(enabled=True)
    filters = SearchFilters(
        external_ids=None,
        metadata=MetadataLogicalConditionGroup(
            combinator="AND",
            negated=False,
            conditions=[
                MetadataLogicalCondition(lhs_variable=Inputs.var1, operator="=", rhs_variable=Inputs.var1),
                MetadataLogicalCondition(lhs_variable=Inputs.var1, operator="=", rhs_variable=Inputs.var1),
            ],
        ),
    )
    chunk_separator = "\n\n#####\n\n"
