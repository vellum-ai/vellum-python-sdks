from vellum import SearchResultMergingRequest, SearchWeightsRequest
from vellum.workflows.nodes.displayable import SearchNode
from vellum.workflows.nodes.displayable.bases.types import MetadataLogicalConditionGroup, SearchFilters

from .most_recent_message import MostRecentMessage


class SearchResults(SearchNode):
    """Here we perform a semantic search on a Vellum Document Index that contains PDFs about Vellum's security policies. As a result, we get chunks from PDFs scored by semantic similarity to the user's query."""

    query = MostRecentMessage.Outputs.result
    document_index = "vellum-security-policies"
    limit = 8
    weights = SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2)
    result_merging = SearchResultMergingRequest(enabled=True)
    filters = SearchFilters(
        external_ids=None, metadata=MetadataLogicalConditionGroup(combinator="AND", negated=False, conditions=[])
    )
    chunk_separator = "\n\n#####\n\n"
