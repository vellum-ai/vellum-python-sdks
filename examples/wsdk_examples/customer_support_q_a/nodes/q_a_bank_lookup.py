from vellum import SearchResultMergingRequest, SearchWeightsRequest
from vellum.workflows.nodes.displayable import SearchNode
from vellum.workflows.nodes.displayable.bases.types import MetadataLogicalConditionGroup, SearchFilters

from ..inputs import Inputs


class QABankLookup(SearchNode):
    query = Inputs.question
    document_index = "vellum-q-a-bank-demos-aezoyg"
    limit = 1
    weights = SearchWeightsRequest(semantic_similarity=0.8, keywords=0.2)
    result_merging = SearchResultMergingRequest(enabled=True)
    filters = SearchFilters(
        external_ids=None, metadata=MetadataLogicalConditionGroup(combinator="AND", negated=False, conditions=[])
    )
    chunk_separator = "#####"
