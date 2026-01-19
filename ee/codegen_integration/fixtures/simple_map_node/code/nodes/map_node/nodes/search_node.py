from vellum import SearchResultMergingRequest, SearchWeightsRequest
from vellum.workflows.nodes.displayable import SearchNode as BaseSearchNode
from vellum.workflows.nodes.displayable.bases.types import SearchFilters

from ..inputs import Inputs


class SearchNode(BaseSearchNode):
    query = Inputs.item
    document_index = "my-sweet-document"
    limit = 8
    weights = SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2)
    result_merging = SearchResultMergingRequest(enabled=True)
    filters = SearchFilters(external_ids=None, metadata=None)
    chunk_separator = "\n\n#####\n\n"

    class Display(BaseSearchNode.Display):
        x = 1909.9521341463415
        y = 212.0475201437282
