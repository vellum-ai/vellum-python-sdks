from vellum import SearchResultMergingRequest, SearchWeightsRequest
from vellum.workflows.nodes.displayable import SearchNode
from vellum.workflows.nodes.displayable.bases.types import SearchFilters

from .most_recent_message import MostRecentMessage


class FAADocumentStore(SearchNode):
    query = MostRecentMessage.Outputs.result
    document_index = "my-sweet-document"
    limit = 8
    weights = SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2)
    result_merging = SearchResultMergingRequest(enabled=True)
    filters = SearchFilters(external_ids=None, metadata=None)
    chunk_separator = "\n\n#####\n\n"
