from vellum import SearchFiltersRequest, SearchRequestOptionsRequest, SearchResultMergingRequest, SearchWeightsRequest
from vellum.workflows.nodes.displayable import SearchNode as BaseSearchNode

from ..inputs import Inputs


class SearchNode(BaseSearchNode):
    query = Inputs.item
    document_index = "my-sweet-document"
    options = SearchRequestOptionsRequest(
        limit=8,
        weights=SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2),
        result_merging=SearchResultMergingRequest(enabled=True),
        filters=SearchFiltersRequest(external_ids=None, metadata=None),
    )
    chunk_separator = "\n\n#####\n\n"
