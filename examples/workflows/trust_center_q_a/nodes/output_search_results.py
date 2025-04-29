from typing import List

from vellum import SearchResult
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .search_results import SearchResults


class OutputSearchResults(FinalOutputNode[BaseState, List[SearchResult]]):
    class Outputs(FinalOutputNode.Outputs):
        value = SearchResults.Outputs.results
