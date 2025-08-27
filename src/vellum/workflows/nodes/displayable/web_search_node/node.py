from typing import Any, ClassVar, Dict, List, Optional

from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.generics import StateType


class WebSearchNode(BaseNode[StateType]):
    """
    Used to perform web search using SerpAPI.

    query: str - The search query to execute
    api_key: str - SerpAPI authentication key
    num_results: int - Number of search results to return (default: 10)
    location: Optional[str] - Geographic location filter for search
    """

    query: ClassVar[str] = ""
    api_key: ClassVar[Optional[str]] = None
    num_results: ClassVar[int] = 10
    location: ClassVar[Optional[str]] = None

    class Outputs(BaseOutputs):
        """
        The outputs of the WebSearchNode.

        text: str - Concatenated search result snippets with titles
        urls: List[str] - List of URLs from search results
        results: List[Dict[str, Any]] - Raw search results from SerpAPI
        """

        text: str
        urls: List[str]
        results: List[Dict[str, Any]]

    def _validate(self) -> None:
        """Validate node inputs.

        TODO: Add validation for query, api_key, and num_results parameters.
        """
        pass

    def run(self) -> Outputs:
        """Run the WebSearchNode to perform web search.

        TODO: Implement web search functionality with SerpAPI integration.
        """
        raise NotImplementedError("WebSearchNode functionality not yet implemented")
