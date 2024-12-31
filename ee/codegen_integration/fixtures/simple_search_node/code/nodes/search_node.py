from vellum import SearchFiltersRequest, SearchRequestOptionsRequest, SearchResultMergingRequest, SearchWeightsRequest
from vellum.types import VellumValueLogicalConditionGroupRequest, VellumValueLogicalConditionRequest
from vellum.workflows.nodes.displayable import SearchNode as BaseSearchNode

from ..inputs import Inputs


class SearchNode(BaseSearchNode):
    query = Inputs.query
    document_index = "my-sweet-document"
    options = SearchRequestOptionsRequest(
        limit=8,
        weights=SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2),
        result_merging=SearchResultMergingRequest(enabled=True),
        filters=SearchFiltersRequest(
            external_ids=None,
            metadata=VellumValueLogicalConditionGroupRequest(
                type="LOGICAL_CONDITION_GROUP",
                combinator="AND",
                negated=False,
                conditions=[
                    VellumValueLogicalConditionRequest(
                        type="LOGICAL_CONDITION", lhs_variable=Inputs.var1, operator="=", rhs_variable=Inputs.var1
                    ),
                    VellumValueLogicalConditionRequest(
                        type="LOGICAL_CONDITION", lhs_variable=Inputs.var1, operator="=", rhs_variable=Inputs.var1
                    ),
                ],
            ),
        ),
    )
    chunk_separator = "\n\n#####\n\n"
