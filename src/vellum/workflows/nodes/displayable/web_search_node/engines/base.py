from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class SearchEngineBase(ABC):
    """
    Abstract base class for search engines used by WebSearchNode.

    All search engines must implement the search method and return
    a normalized response format compatible with WebSearchNode.Outputs.
    """

    @abstractmethod
    def search(
        self,
        query: str,
        api_key: str,
        num_results: int,
        location: Optional[str],
        context: Any,
    ) -> Dict[str, Any]:
        """
        Execute search and return normalized response.

        Args:
            query: The search query to execute
            api_key: API authentication key
            num_results: Number of search results to return
            location: Optional geographic location filter
            context: WorkflowContext for accessing vellum_client

        Returns:
            Dict containing:
                - text: str - Formatted search result text
                - urls: List[str] - List of result URLs
                - results: List[Dict[str, Any]] - Raw search results

        Raises:
            NodeException: For validation, authentication, or API errors
        """
        pass
