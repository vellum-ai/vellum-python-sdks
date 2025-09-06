import logging
from typing import Any, ClassVar, Dict, List, Optional

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.types.generics import StateType

from .engines.factory import SearchEngineFactory

logger = logging.getLogger(__name__)


class WebSearchNode(BaseNode[StateType]):
    """
    Used to perform web search using configurable search engines.

    query: str - The search query to execute
    api_key: str - Search engine authentication key
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
        results: List[Dict[str, Any]] - Raw search results from search engine
        """

        text: str
        urls: List[str]
        results: List[Dict[str, Any]]

    def _validate(self) -> None:
        """Validate node inputs."""
        if not self.query or not isinstance(self.query, str) or not self.query.strip():
            raise NodeException(
                "Query is required and must be a non-empty string", code=WorkflowErrorCode.INVALID_INPUTS
            )

        if self.api_key is None:
            raise NodeException("API key is required", code=WorkflowErrorCode.INVALID_INPUTS)

        if not isinstance(self.num_results, int) or self.num_results <= 0:
            raise NodeException("num_results must be a positive integer", code=WorkflowErrorCode.INVALID_INPUTS)

    def run(self) -> Outputs:
        """Run the WebSearchNode to perform web search via search engine."""
        self._validate()

        # Use SerpAPI engine for Phase 1 - maintains exact same functionality
        search_engine = SearchEngineFactory.create_engine("serpapi")

        result = search_engine.search(
            query=self.query,
            api_key=self.api_key,
            num_results=self.num_results,
            location=self.location,
            context=self._context,
        )

        return self.Outputs(
            text=result["text"],
            urls=result["urls"],
            results=result["results"],
        )
